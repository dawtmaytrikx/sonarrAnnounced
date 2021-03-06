import datetime
import logging

import config
import db
import sonarr
import radarr
import utils

cfg = config.init()

############################################################
# Tracker Configuration
############################################################
name = "RevolutionTT"
irc_host = "irc.revolutiontt.me"
irc_port = 7000
irc_channel = "#announce"
invite_cmd = "RevoTT !invite " + cfg["{}.nick".format(name.lower())]
irc_tls = True
irc_tls_verify = False

# these are loaded by init
auth_key = None
torrent_pass = None

logger = logging.getLogger(name.upper())
logger.setLevel(logging.DEBUG)


############################################################
# Tracker Framework (all trackers must follow)
############################################################
# Parse announcement message
@db.db_session
def parse(announcement):
    global name

    decolored = utils.strip_irc_color_codes(announcement)
    if '!new ' not in decolored:
        return

    # extract required information from announcement
    torrent_title = utils.replace_spaces(utils.substr(decolored, '!new ', ' | ', True), '.')
    torrent_id = utils.substr(decolored, '?id=', '&', True)
    
    if '| TV/' in decolored:
        notify_pvr(torrent_id, torrent_title, auth_key, torrent_pass, name, 'Sonarr')
    elif '| Movies/' in decolored:
        notify_pvr(torrent_id, torrent_title, auth_key, torrent_pass, name, 'Radarr')



def notify_pvr(torrent_id, torrent_title, auth_key, torrent_pass, name, pvr_name):
    if torrent_id is not None and torrent_title is not None:
        download_link = get_torrent_link(torrent_id, torrent_title)

        announced = db.Announced(date=datetime.datetime.now(), title=torrent_title,
                                 indexer=name, torrent=download_link, pvr=pvr_name)
                                 
        if pvr_name == 'Sonarr':
            approved = sonarr.wanted(torrent_title, download_link, name)
        elif pvr_name == 'Radarr':
            approved = radarr.wanted(torrent_title, download_link, name)
            
        if approved:
            logger.debug("%s approved release: %s", pvr_name, torrent_title)
            snatched = db.Snatched(date=datetime.datetime.now(), title=torrent_title,
                                   indexer=name, torrent=download_link, pvr=pvr_name)
        else:
            logger.debug("%s rejected release: %s", pvr_name, torrent_title)
    
    return
                

# Generate torrent link
def get_torrent_link(torrent_id, torrent_name):
    torrent_link = "https://revolutiontt.me/download.php/{}/{}.torrent?passkey={}".format(torrent_id,
                                                                                            torrent_name,
                                                                                            torrent_pass)
    return torrent_link


# Initialize tracker
def init():
    global auth_key, torrent_pass

    auth_key = cfg["{}.auth_key".format(name.lower())]
    torrent_pass = cfg["{}.torrent_pass".format(name.lower())]

    # check torrent_pass was supplied
    if not torrent_pass:
        return False

    return True
