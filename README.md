# fidelitybooks

My client received html and css files for his website from a graphic designer and I was tasked with turning that into a eBook store with full functionality.

I built the entire app using the Flask framework with python. This involved:
 - configuring the PayPal IPN (instant payment notification listener)
 - setting up the purchase engine to auto email the customers with a download link
 - configuring the postgresql database to store download keys and delete the key after a single use
 - depoloying to heroku
 - walking the client through the handover document to ensure he could easily add new books to his store and edit thing as he wished without breaking anything
