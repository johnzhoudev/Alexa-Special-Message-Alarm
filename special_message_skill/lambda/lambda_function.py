# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.api_client import DefaultApiClient

from ask_sdk_model.services.directive import send_directive_request
from ask_sdk_model.interfaces.tasks.complete_task_directive import CompleteTaskDirective
from ask_sdk_model.interfaces.audioplayer.play_directive import PlayDirective
from ask_sdk_model.interfaces.audioplayer.audio_item import AudioItem
from ask_sdk_model.interfaces.audioplayer.stream import Stream
from ask_sdk_model.interfaces.audioplayer.play_behavior import PlayBehavior

from ask_sdk_core.skill_builder import SkillBuilder, CustomSkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

from utils import get_audio, get_amazon_user_id, NO_FILES_UPLOADED

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Consts, should move to param store?
ROLE_ARN = "arn:aws:iam::170221608339:role/special_message_alarm_lambda_execution_role"
REGION_NAME = "us-east-1"
S3_BUCKET = "special-message-alarm-audio-bucket"
DYNAMO_TABLE_NAME = "special-message-alarm-audio-state"

class LaunchRequestHandler(AbstractRequestHandler):
  """Handler for Skill Launch."""
  def can_handle(self, handler_input):
    # type: (HandlerInput) -> bool

    return ask_utils.is_request_type("LaunchRequest")(handler_input)

  def handle(self, handler_input):
    # type: (HandlerInput) -> Response
    speak_output = "Welcome to the special message alarm skill! Say help for more info."
    error_output = "Unexpected error encountered. Fuuuk."
    upload_items_output = "Error, you currently have no audio files uploaded. Please upload them on S3 thru the AWS developer console"
    print("user id", get_amazon_user_id(handler_input))

    # def get_audio(role_arn, region_name, s3_bucket, dynamo_table_name, amazon_user_id):
    audio_url, audio_token = get_audio(ROLE_ARN, REGION_NAME, S3_BUCKET, DYNAMO_TABLE_NAME, get_amazon_user_id(handler_input))
    print(audio_url)

    if (audio_url is None):
      return (handler_input.response_builder
        .speak(error_output)
        .response)
    elif (audio_url == NO_FILES_UPLOADED):
      return (handler_input.response_builder
        .speak(upload_items_output)
        .response)

    audio_item = AudioItem(
      stream=Stream(
        url=audio_url,
        token=audio_token,
        offset_in_milliseconds=0
      )
    )

    play_directive = PlayDirective(
      play_behavior=PlayBehavior.REPLACE_ALL,
      audio_item=audio_item
    )

    return (
      handler_input.response_builder
        .add_directive(play_directive)
        .response
    )

class HelloWorldIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HelloWorldIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "I'm sorry I'm such a fuking piece of shhhit"

        print(handler_input.response_builder.speak(speak_output).response)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = """To play a special message alarm, the special message should play when you 
          say the open command open special message alarm. Use a routine to invoke this skill and set the routine at a 
          specific time to make it play.
        """

        ask_output = "Is there anything else I can help with? You can say help again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelloWorldIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()