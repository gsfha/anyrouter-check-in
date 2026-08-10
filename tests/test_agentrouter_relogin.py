import pytest

from checkin import GITHUB_SESSION_COOKIE_NAMES, check_in_account, select_cookies
from utils.config import AccountConfig, AppConfig


def test_select_cookies_keeps_only_github_session_material():
	selected = select_cookies(
		'user_session=session-value; _gh_sess=csrf-value; theme=dark; logged_in=yes',
		GITHUB_SESSION_COOKIE_NAMES,
	)

	assert selected == {
		'user_session': 'session-value',
		'_gh_sess': 'csrf-value',
		'logged_in': 'yes',
	}


def test_select_cookies_rejects_unrelated_cookie_only():
	assert select_cookies('theme=dark; tz=UTC', GITHUB_SESSION_COOKIE_NAMES) == {}


@pytest.mark.asyncio
async def test_agentrouter_site_cookie_is_not_reported_as_checkin_success(monkeypatch, capsys):
	monkeypatch.delenv('PROVIDERS', raising=False)
	account = AccountConfig(
		name='AgentRouter stale method',
		provider='agentrouter',
		cookies={'session': 'site-session'},
		api_user='12345',
	)

	success, before, after = await check_in_account(account, 0, AppConfig.load_from_env())

	assert success is False
	assert before is None
	assert after is None
	assert 'checks in only during re-login' in capsys.readouterr().out
