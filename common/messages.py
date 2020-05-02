
class Errors:
    NO_USERNAME = 'You need a telegram handle/ username before using the bot.'
    BAN_MESSAGE = 'You have been banned, please contact administrator for help.'
    INCORRECT_TIME = (
        'Preferred time could not be recognized.\n'
        'Please enter a time that is past and within 24 hours of %s.'
    )
    LENGTH_TOO_LONG = 'Message length is too long, please keep within 250 characters.'
    GENERIC_ERROR = 'Error encountered please contact adminstrator.'
    NO_REQUEST_FOUND = 'Seems like your request has expired, please repost! /start'
    NO_LONGER_ACTIVE = 'Match is no longer active'
    SEARCH_ERROR = (
        '/search_dropoff or /search_pickup must be followed by the location itself.\n'
        'eg. /search_dropoff Clementi MRT'
    )

class Messages:
    ADDITIONAL_INFO_REQUEST = (
        'Any additional information?\n'
        'eg. time constraints, payment constraints'
    )
    LOCATION_PICKUP_REQUEST = 'Now, what is your pickup location?'
    LOCATION_DROPOFF_REQUEST = 'What is your dropoff location?'
    LOCATION_NUM_DROPOFF_REQUEST = 'How many dropoffs do you have?'
    PRICE_REQUEST = 'What is your preferred price? eg. 10.50, 20'
    TIME_REQUEST = 'What is your preferred time for pickup? eg. 10pm, 9:10am'
    PACKAGE_REQUEST = 'Describe your package!'
    THANK_YOU_MESSAGE = 'Thank you! We are now processing your ticket!'
    WELCOME_MESSAGE = (
        'Welcome to the Hitch Matching bot!'
        ' Please use /help to get a short introduction'
    )
    HELP_MESSAGE = (
        'Hitch Match Bot matches a driver to a customer when both parties have accepted each other.'
        '\n\n'
        'This list will be cleaned after every hour to make sure that no requests here are stale.'
        '\n\n'
        'Once your request ticket has been created for driver/ customer, you may refresh the list'
        ' using /list to see all available listings.'
    )
    POST_ADDITIONAL_INFO_REQUEST = (
        'Now use /list to list down all available requests or use the /search_dropoff or the '
        '/search_pickup commands to refine your search.\n\n'
        'eg. /search_pickup Clementi MRT'
    )
