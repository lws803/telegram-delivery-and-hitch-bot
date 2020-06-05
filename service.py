import json
import logging
import os
from datetime import datetime

import telegram.ext
from dateutil import tz
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)

import parsedatetime
from common.constants import RegExpressions, RoleType, StateType
from common.exceptions import NoUserNameException, UserBannedException
from common.messages import Errors, Messages
from common.models import Report, Request
from common.mysql_connector import MySQLConnector
from helpers.filters import ResultFilters
from helpers.helpers import (check_blacklist, check_request_exists,
                             check_search_user_valid, get_location,
                             get_location_json, get_locations_json)
from matcher.matcher import Matcher

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

matcher_session = Matcher()
mysql_connector = MySQLConnector()

## Prod bot
updater = Updater(os.environ.get('TELE_KEY_PROD'), use_context=True)

# Get the dispatcher to register handlers
dp = updater.dispatcher
bot = updater.bot


(
    ROLE, LOCATION_PICKUP, NUM_DROPOFFS, LOCATION_DROPOFF,
    PRICE, TIME, PACKAGE_TYPE, ADDITIONAL_INFO
) = range(8)


def listing_formatter(request):
    if request.role == RoleType.DRIVER:
        return (
            '*Driver*\n'
            f'{request.first_name}\n'
            'Additional information:\n'
            f'{request.additional_info}'
        )
    to_zone = tz.gettz(os.environ['TZ'])
    utc = tz.gettz('utc')

    time_format = (
        request.time.replace(tzinfo=utc).astimezone(to_zone).strftime('%d, %b %Y %I:%M %p')
    )
    pickup_location = json.loads(request.location_pickup)['text']
    dropoff_locations = json.loads(request.location_dropoffs)
    dropoff_text = 'Dropoffs:'
    for count, dropoff_location in enumerate(dropoff_locations, start=1):
        dropoff_text += '\n{}) {}'.format(count, dropoff_location['text'])

    return (
        '*Customer*\n'
        f'{request.first_name}\n'
        f'Pickup: {pickup_location}\n'
        f'{dropoff_text}\n'
        f'Time: {time_format}\n'
        f'Price: {request.price}\n'
        f'Package info: {request.package_type}\n'
        'Additional information:\n'
        f'{request.additional_info}'
    )


def validate_add_to_db(context, update):
    user = update.message.from_user
    chat_id = update.message.chat_id

    if not user.username:
        raise NoUserNameException

    with mysql_connector.session() as db_session:
        existing_entry = (
            db_session
            .query(Request)
            .filter_by(chat_id=chat_id)
            .one_or_none()
        )
        if existing_entry:
            # Disabled flood checks
            db_session.delete(existing_entry)
            db_session.commit()

        if context.chat_data['role'] == 'Driver':
            new_request = Request(
                chat_id=chat_id,
                additional_info=context.chat_data['additional_info'],
                state=StateType.ACTIVE,
                role=RoleType.DRIVER,
                first_name=user.first_name,
                last_name=user.last_name,
                telegram_handle=user.username
            )
        else:
            new_request = Request(
                location_pickup=get_location_json(context.chat_data['location_pickup']),
                location_dropoffs=get_locations_json(context.chat_data['location_dropoffs']),
                chat_id=chat_id,
                additional_info=context.chat_data['additional_info'],
                state=StateType.ACTIVE,
                time=context.chat_data['time'],
                price=context.chat_data['price'],
                package_type=context.chat_data['package_type'],
                role=RoleType.CUSTOMER,
                first_name=user.first_name,
                last_name=user.last_name,
                telegram_handle=user.username
            )

        db_session.add(new_request)
        db_session.commit()
        update.message.reply_text(
            'Your request has been created\n\n' + listing_formatter(new_request),
            parse_mode=telegram.ParseMode.MARKDOWN
        )


def start(update, context):
    user = update.message.from_user
    with mysql_connector.session() as db_session:
        try:
            check_blacklist(db_session, update.message.chat_id)
        except UserBannedException as e:
            update.message.reply_text(str(e))
            logger.info("User %s was blacklisted and tried to access bot.", user.first_name)
            return ConversationHandler.END
        except Exception:
            return ConversationHandler.END


    reply_keyboard = [['Driver', 'Hitcher or Customer']]
    update.message.reply_text(Messages.WELCOME_MESSAGE)
    update.message.reply_text(
        'State your role',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return ROLE


def role(update, context):
    user = update.message.from_user
    logger.info('Role of %s: %s', user.first_name, update.message.text)
    context.chat_data['role'] = update.message.text

    if context.chat_data['role'] == 'Driver':
        update.message.reply_text(
            Messages.ADDITIONAL_INFO_REQUEST,
            reply_markup=ReplyKeyboardRemove()
        )
        return ADDITIONAL_INFO

    update.message.reply_text(
        Messages.LOCATION_PICKUP_REQUEST,
        reply_markup=ReplyKeyboardRemove()
    )
    return LOCATION_PICKUP


def location_pickup(update, context):
    user = update.message.from_user

    if len(update.message.text) >= 250:
        update.message.reply_text(Errors.LENGTH_TOO_LONG)
        return LOCATION_PICKUP

    user_location = update.message.text
    logger.info('Location of %s: %s', user.first_name, update.message.text)

    context.chat_data['location_pickup'] = user_location

    update.message.reply_text(Messages.LOCATION_NUM_DROPOFF_REQUEST)
    context.chat_data['location_dropoffs'] = []  # Clear the data if there are any
    return NUM_DROPOFFS


def num_dropoffs(update, context):
    user = update.message.from_user
    logger.info('Number of dropoffs for %s: %s', user.first_name, update.message.text)
    context.chat_data['num_dropoffs'] = int(update.message.text)
    update.message.reply_text(Messages.LOCATION_DROPOFF_REQUEST)
    return LOCATION_DROPOFF


def location_dropoff(update, context):
    user = update.message.from_user

    if len(update.message.text) >= 250:
        update.message.reply_text(Errors.LENGTH_TOO_LONG)
        return LOCATION_DROPOFF

    user_location = update.message.text
    logger.info('Location of %s: %s', user.first_name, update.message.text)

    if 'location_dropoffs' not in context.chat_data:
        context.chat_data['location_dropoffs'] = [user_location]
    else:
        context.chat_data['location_dropoffs'].append(user_location)

    if len(context.chat_data['location_dropoffs']) < context.chat_data['num_dropoffs']:
        update.message.reply_text(Messages.LOCATION_DROPOFF_REQUEST_NEXT)
        return LOCATION_DROPOFF

    update.message.reply_text(Messages.PRICE_REQUEST)
    return PRICE


def price(update, context):
    user = update.message.from_user
    logger.info('Price of %s: %s', user.first_name, update.message.text)
    context.chat_data['price'] = float(update.message.text)
    update.message.reply_text(Messages.TIME_REQUEST)

    return TIME


def time(update, context):
    user = update.message.from_user
    cal = parsedatetime.Calendar()
    utc = tz.gettz('utc')

    time_struct, parse_status = cal.parse(update.message.text)
    local_time = datetime(*time_struct[:6])
    utc_time = local_time.astimezone(utc)
    if not parse_status:
        update.message.reply_text(
            Errors.INCORRECT_TIME
        )
        return TIME

    context.chat_data['time'] = utc_time

    logger.info(
        'Time of %s at %s',
        user.first_name,
        str(utc_time)
    )
    update.message.reply_text(Messages.PACKAGE_REQUEST)

    return PACKAGE_TYPE


def package_type(update, context):

    if len(update.message.text) >= 250:
        update.message.reply_text(Errors.LENGTH_TOO_LONG)
        return PACKAGE_TYPE

    context.chat_data['package_type'] = update.message.text

    update.message.reply_text(Messages.ADDITIONAL_INFO_REQUEST)
    return ADDITIONAL_INFO


def additional_info(update, context):
    user = update.message.from_user
    logger.info("Additional info of %s: %s", user.first_name, update.message.text)

    if len(update.message.text) >= 250:
        update.message.reply_text(Errors.LENGTH_TOO_LONG)
        return ADDITIONAL_INFO

    context.chat_data['additional_info'] = update.message.text

    context.job_queue.run_once(process_request, 0, context=(update, context))
    update.message.reply_text(Messages.THANK_YOU_MESSAGE)

    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    with mysql_connector.session() as db_session:
        my_request = db_session.query(Request).filter_by(chat_id=update.message.chat_id).one_or_none()
        if my_request:
            my_request.state = StateType.DONE
        db_session.commit()

    update.message.reply_text('Canceled',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def help_me(update, context):
    user = update.message.from_user
    # FIXME: Move this with mysql_connector.session() as db_session: chunk to another method
    # wrap it with retry connection
    with mysql_connector.session() as db_session:
        try:
            check_blacklist(db_session, update.message.chat_id)
        except UserBannedException as e:
            update.message.reply_text(str(e))
            logger.info("User %s was blacklisted and tried to access bot.", user.first_name)
            return ConversationHandler.END
        except Exception:
            return ConversationHandler.END

    update.message.reply_text(Messages.HELP_MESSAGE,
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def list_all(update, context):
    user = update.message.from_user
    logger.info("User %s refreshed the list.", user.first_name)

    update.message.reply_text('Refreshing...',
                              reply_markup=ReplyKeyboardRemove())

    context.job_queue.run_once(refresh_handler, 0, context=(update, context))

    return ConversationHandler.END


def search_pickup(update, context):
    args = context.args
    user = update.message.from_user
    logger.info(
        "User {} searching the list for dropoffs that match. {}".format(user.first_name, str(args))
    )

    update.message.reply_text('Searching... {}'.format(' '.join(args)),
                              reply_markup=ReplyKeyboardRemove())

    context.job_queue.run_once(search_handler, 0, context=(update, context, 'pickup'))

    return ConversationHandler.END


def search_dropoff(update, context):
    args = context.args
    user = update.message.from_user
    logger.info(
        "User {} searching the list for pickups that match. {}".format(user.first_name, str(args))
    )

    update.message.reply_text('Searching... {}'.format(' '.join(args)),
                              reply_markup=ReplyKeyboardRemove())

    context.job_queue.run_once(search_handler, 0, context=(update, context, 'dropoff'))

    return ConversationHandler.END


def search_handler(context: telegram.ext.CallbackContext):
    update, context, search_type = context.job.context
    if not context.args:
        update.message.reply_text(Errors.SEARCH_ERROR)
        return
    with mysql_connector.session() as db_session:
        try:
            check_request_exists(db_session, update)
            check_search_user_valid(db_session, update)
        except Exception:
            return

    location_dict = get_location(' '.join(context.args))
    if search_type == 'dropoff':
        get_relevant_requests(update, context, dropoff_dict=location_dict)
    else:
        get_relevant_requests(update, context, pickup_dict=location_dict)


def refresh_handler(context: telegram.ext.CallbackContext):
    update, context = context.job.context
    with mysql_connector.session() as db_session:
        try:
            check_request_exists(db_session, update)
        except Exception:
            return

    get_relevant_requests(update, context)


def get_relevant_requests(update, context, pickup_dict=None, dropoff_dict=None):
    with mysql_connector.session() as db_session:
        curr_request = (
            db_session.query(Request)
            .filter_by(
                chat_id=update.message.chat_id,
                state=StateType.ACTIVE,
            )
            .one_or_none()
        )
        context.chat_data['chat_id'] = update.message.chat_id

        all_relevant_requests = (
            db_session.query(Request)
            .filter_by(
                role=(
                    RoleType.CUSTOMER if curr_request.role == RoleType.DRIVER else RoleType.DRIVER
                ),
                state=StateType.ACTIVE,
            )
            .all()
        )

        if pickup_dict or dropoff_dict:
            all_relevant_requests = ResultFilters.filter_location(
                all_relevant_requests,
                coordinates_pickup=pickup_dict['latlng'] if pickup_dict else None,
                coordinates_dropoff=dropoff_dict['latlng'] if dropoff_dict else None
            )

        update.message.reply_text(f'We have {len(all_relevant_requests)} requests now...')

        for request in all_relevant_requests:
            keyboard = [
                [
                    InlineKeyboardButton("Accept", callback_data=f'accept:{request.chat_id}'),
                    InlineKeyboardButton("Ignore", callback_data=f'ignore:{request.chat_id}')
                ],
                [InlineKeyboardButton("Report", callback_data=f'report:{request.chat_id}')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(
                f'{listing_formatter(request)}', reply_markup=reply_markup,
                parse_mode=telegram.ParseMode.MARKDOWN
            )


def process_request(context: telegram.ext.CallbackContext):
    update, context = context.job.context
    try:
        validate_add_to_db(context, update)

    except NoUserNameException:
        update.message.reply_text(Errors.NO_USERNAME)
        return

    except Exception as e:
        update.message.reply_text(Errors.GENERIC_ERROR)
        logger.warning(str(e))
        return

    update.message.reply_text(Messages.POST_ADDITIONAL_INFO_REQUEST)


def button(update, context):
    query = update.callback_query
    choice, chat_id = query.data.split(':')[0], int(query.data.split(':')[1])

    def reply_not_active():
        query.answer()
        query.edit_message_text(text=Errors.NO_LONGER_ACTIVE)

    request = None
    with mysql_connector.session() as db_session:
        request = (
            db_session.query(Request)
            .filter_by(
                chat_id=chat_id,
                state=StateType.ACTIVE
            )
            .one_or_none())

        if choice == 'report':
            existing_report = db_session.query(Report).filter_by(chat_id=chat_id).one_or_none()
            if existing_report:
                existing_report.report_count += 1
            else:
                db_session.add(Report(chat_id=chat_id, report_count=1))
            db_session.commit()
            query.answer()
            query.edit_message_text(text='Your feedback has been reported!')
            return

        elif choice == 'accept':
            matcher_session.add_match(context.chat_data['chat_id'], chat_id)
            if matcher_session.check_match(context.chat_data['chat_id'], chat_id):
                my_request = (
                    db_session.query(Request)
                    .filter_by(chat_id=context.chat_data['chat_id'])
                    .one_or_none()
                )
                if request and my_request:
                    try:
                        bot.send_message(
                            chat_id=context.chat_data['chat_id'],
                            text=f'Match found! @{request.telegram_handle}'
                        )
                        bot.send_message(
                            chat_id=chat_id,
                            text=f'Match found! @{my_request.telegram_handle}'
                        )
                        # Cleanup
                        matcher_session.delete_match(chat_id, context.chat_data['chat_id'])
                    except Exception as e:
                        logger.warning(str(e))
                else:
                    reply_not_active()
                    return

        if request:
            query.answer()
            query.edit_message_text(
                text=f'{listing_formatter(request)}\n\n{choice}!',
                parse_mode=telegram.ParseMode.MARKDOWN
            )
        else:
            reply_not_active()


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    location_info_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('list', list_all),
            CommandHandler('search_dropoff', search_dropoff),
            CommandHandler('search_pickup', search_pickup),
            CommandHandler('cancel', cancel),
            CommandHandler('help', help_me)
        ],
        states={
            ROLE: [MessageHandler(Filters.regex(r'^(Driver|Hitcher or Customer)$'), role)],
            LOCATION_PICKUP: [
                MessageHandler(Filters.regex(RegExpressions.NO_COMMAND_SLASH), location_pickup)
            ],
            NUM_DROPOFFS: [MessageHandler(Filters.regex(RegExpressions.NUMBER), num_dropoffs)],
            LOCATION_DROPOFF: [
                MessageHandler(Filters.regex(RegExpressions.NO_COMMAND_SLASH), location_dropoff)
            ],
            PRICE: [
                MessageHandler(Filters.regex(RegExpressions.PRICE), price)
            ],
            TIME: [MessageHandler(Filters.regex(RegExpressions.NO_COMMAND_SLASH), time)],
            PACKAGE_TYPE: [
                MessageHandler(Filters.regex(RegExpressions.NO_COMMAND_SLASH), package_type)
            ],
            ADDITIONAL_INFO: [
                MessageHandler(Filters.regex(RegExpressions.NO_COMMAND_SLASH), additional_info)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(location_info_handler)
    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
