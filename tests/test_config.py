from utils.config import config, save_config, load_config


def test_load_config():
    assert config.auth.secret != ""


def test_save_config():
    tmp = config.auth.secret
    config.auth.secret = "test"
    save_config()
    load_config()
    assert config.auth.secret == "test"
    config.auth.secret = tmp
    save_config()
    load_config()
    assert config.auth.secret == tmp
