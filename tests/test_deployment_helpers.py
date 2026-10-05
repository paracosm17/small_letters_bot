import pytest

from scripts.coolify_deploy_api import (
    ImmutableImage,
    normalize_base_url,
    parse_image_reference,
)


def test_parse_immutable_image():
    digest = "a" * 64
    image = parse_image_reference(f"ghcr.io/paracosm17/small_letters_bot@sha256:{digest}")
    assert image == ImmutableImage(
        name="ghcr.io/paracosm17/small_letters_bot",
        digest=digest,
    )
    assert image.coolify_tag == f"sha256-{digest}"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/api/v1",
        "http://203.0.113.10:8000/api/v1",
        "http://127.0.0.1:9000/api/v1",
    ],
)
def test_coolify_helper_rejects_non_loopback_api(url):
    with pytest.raises(ValueError):
        normalize_base_url(url)


def test_coolify_helper_accepts_fixed_tunnel():
    assert normalize_base_url("http://127.0.0.1:18000/api/v1") == "http://127.0.0.1:18000/api/v1"
