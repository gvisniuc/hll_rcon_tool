from dateutil import parser
from django.views.decorators.csrf import csrf_exempt

from rcon.utils import MapsHistory
from rcon.recorded_commands import RecordedRcon
from rcon.commands import CommandFailedError
from rcon.steam_utils import get_steam_profile
from rcon.settings import SERVER_INFO
from .auth import login_required, api_response, api_csv_response
from .utils import _get_data
from rcon import game_logs
from rcon.models import LogLine, PlayerSteamID, PlayerName, enter_session
from sqlalchemy import or_, and_


@csrf_exempt
@login_required
def get_historical_logs(request):
    data = _get_data(request)
    player_name = data.get("player_name")
    action = data.get("log_type")
    steam_id_64 = data.get("steam_id_64")
    limit = int(data.get("limit", 1000))
    from_ = data.get("from")
    till = data.get("till")
    time_sort = data.get("time_sort", "desc")
    exact_player_match = data.get("exact_player", False)
    exact_action = data.get("exact_action", True)
    server_filter = data.get("server_filter")
    output = data.get("output")

    if till:
        till = parser.parse(till)
    if from_:
        from_ = parser.parse(from_)

    lines = game_logs.get_historical_logs(
        player_name=player_name,
        action=action,
        steam_id_64=steam_id_64,
        limit=limit,
        from_=from_,
        till=till,
        time_sort=time_sort,
        exact_player_match=exact_player_match,
        exact_action=exact_action,
        server_filter=server_filter,
        output=output
    )
    if output != "CSV" and output != "csv":
        return api_response(
            lines,
            command="get_historical_logs",
            arguments=dict(limit=limit, player_name=player_name, action=action),
            failed=False,
        )
    return api_csv_response(lines, "log.csv",
                        ["event_time", "type", "player_name", "player1_id",
                        "player2_name", "player2_id", "content", "server", "weapon"])
     
@csrf_exempt
@login_required
def get_recent_logs(request):
    data = _get_data(request)
    start = int(data.get("start", 0))
    end = int(data.get("end", 10000))
    player_search = data.get("filter_player")
    action_filter = data.get("filter_action")
    exact_player_match = data.get("exact_player_match", True)
    exact_action = data.get("exact_action", False)

    return api_response(
        result=game_logs.get_recent_logs(
            start=start,
            end=end,
            player_search=player_search,
            action_filter=action_filter,
            exact_player_match=exact_player_match,
            exact_action=exact_action,
        ),
        command="get_recent_logs",
        arguments=dict(
            start=start,
            end=end,
            filter_player=player_search,
            filter_action=action_filter,
        ),
        failed=False,
    )
