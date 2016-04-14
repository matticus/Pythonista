# Pythonista
Projects built to run in Pythonista on iOS

MarketResearchPublisher.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
This project was created to streamline the process of distributing Market Research to multiple channels.  I regularly have URLs and commentary that need to be shared with:
	- Company internal Hipchat room
	- Community Slack channels
	- and my Twitter feed (@mhowell)
	
After trying to simplify this workflow on my phone with Launchpad Pro & x-callback-url, I found the process was still manual, requiring visits to multiple apps.
This project removes the apps from the equation and instead goes straight to each service's Web API.

Workflow Outline
~~~~~~~~~~~~~~~~
When run, this project:
	- Pulls the current clipboard contents (expecting a URL), and prompts the user to confirm it is the correct URL
	- Asks the user for commentary on the URL (if no commentary is provided, the Page Title of the URL is used)
	- The destination URL is then passed through bit.ly, creating a Short URL to report on visits
	- The combined post is then presented for preview.
	- Finally, prior to posting, the user is asked whether the post should go to internal Hipchat, or all channels
	- TODO: I am working on also writing the post to a history document in Dropbox, for reporting purposes.

Getting Started
~~~~~~~~~~~~~~~
All configuration is below in the "Configuration section".  You will need to setup / add your own credentials / tokens for each of the supported services.
