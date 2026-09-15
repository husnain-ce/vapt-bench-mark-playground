from flask import Flask, jsonify, render_template, Response

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/initialize")
def initialize():
    return jsonify({"activateAutoRefresh":True,"autoRefreshTimeout":12000000,"bounce":False,"button":False,"defaultSelectorColor":"#00d8a6","enableAutoRefresh":True,"enableFaviconNotification":True,"enableNPS":True,"enableSoundNotification":True,"enableUpdatesListener":True,"enabled":True,"feedbackButton":True,"feedbackButtonColor":"#000000","feedbackButtonPosition":"right","feedbackButtonText":"Feedback","feedbackButtonTextColor":"#ffffff","filterByUrl":True,"hasGA4TrackingId":True,"headerColor":"#3d50e0","ideasEnabled":True,"lastPostBoostedBackgroundColor":"#18181a","lastPostBoostedTextColor":"#ffffff","logoUrl":"https://static.getbeamer.com/mZXqptmd65/logo_small_785.png","notificationColor":"#ff5a5f","npsShowForUrls":["https://app.getbeamer.com/home"],"pushBodyBackgroundColor":"#ffffff","pushBodyTextColor":"#000000","pushNotificationsPrompt":"We'd like to show you notifications for the latest news and updates.","pushNotificationsPromptAccept":"Allow","pushNotificationsPromptEnabled":True,"pushNotificationsPromptRefuse":"No, thanks","pushNotificationsPromptType":"sidebar","pushPrimaryButtonBackgroundColor":"#007aff","pushPrimaryButtonTextColor":"#ffffff","pushSecondaryButtonTextColor":"#8da2b5","roadmapEnabled":True,"showLinkInSnippet":True,"showNPSDelay":10000,"topDomain":"getbeamer.com","updatesDelay":600000})

# The following routes are not part of the challenge. I just don't want to make request to getbeamer.com
@app.route("/beamer-embed.js")
def beamer_embed():
    with open("beamer-embed.js", "r") as file:
        content = file.read()
        content = content.replace("https://app.getbeamer.com/", "/static/")
        content = content.replace("https://push.getbeamer.com/", "/")
        content = content.replace("https://static.getbeamer.com/", "/static/")
        content = content.replace("https://backend.getbeamer.com/", "/")

    return Response(content, mimetype="application/javascript")

@app.route("/numberFeatures")
def numberFeatures():
    return jsonify({"callbackNumber":0,"number":0,"priority":False})

@app.route("/embeddedPush")
def embeddedPush():
    return ""

@app.route("/realtimeUpdates")
def realtimeUpdates():
    return jsonify({"callbackNumber":0,"number":0,"priority":False})

if __name__ == "__main__":
    app.run("0.0.0.0", 5000, debug=True)
