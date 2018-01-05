# hackerdoor

Door code.

## Googleapi/memberlist.py

A proof-of-concept to pull information from a google spreadsheet. This will eventually be used to create a list of cards to add, activate, or deactivate.

### Requirements

install the Google API python client: `pip install --upgrade google-api-python-client`

Requires a configs/hackerdoor-servicecredentials.json file containing the Service API Account credentials for the google sheet you want to access. It is in the shape of:

```
{
  "type": "service_account",
  "project_id": "foo",
  "private_key_id": "foo",
  "private_key": "foo",
  "client_email": "foo@bar.com",
  "client_id": "1234",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "foo"
}
```

### Running

Simply call `python googleapi/memberlist.py` to run the small script. It will pull the current active member members and their card information, such as:

```
Name, Status, FC, CC, Dec
Harry Hacker, ACTIVE, 22, 33, 000001234
Margert Maker, ACTIVE, 00, 11, 000004567
```

The FC, CC, and DEC are components of the card number. The DEC is the decimal equivalent of the FC and CC values.
