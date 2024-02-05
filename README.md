# SensCritique2Trakt
Convert any senscritique.com list to trakt list

Just edit ```SENS_CRITIQUE_URL = 'URL_OF_SENSCRITIQUE_LIST'``` at beginning oki the script to provide your [senscritique.com](https://www.senscritique.com/) list url.

You will need to create a new API app in your [trakt profile](https://trakt.tv/oauth/applications).

Also edit [line 98 to 100] ```"trakt-api-key": "YOUR_TRAKT_API",``` and ```"Authorization": f"Bearer YOUR_TRAKT_TOKEN",``` to provide your trakt.tv api and token.
You can use the provided [trakt_auth.py](https://github.com/PierreDurrr/SensCritique2Trakt/blob/master/trakt_auth.py) trakt_auth.py to get you credentials.

Then, fire the magic !
