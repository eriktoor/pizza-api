# (864) 721-9072
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from orderPizza import order_pizza, app_options, get_menu, intro

app = Flask(__name__)


@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    # Start our TwiML response
    resp = MessagingResponse()

    # Determine the right reply for this message
    message = order_pizza(body)
    resp.message(message)

    return str(resp) if resp else "NA"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)  # host= '0.0.0.0'
