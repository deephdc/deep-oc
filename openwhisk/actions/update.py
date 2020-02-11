import os
import os.path
import subprocess


def main(args):
    ow_host = os.environ.get("__OW_API_HOST")
    ow_namespace = os.environ.get("__OW_NAMESPACE")
    ow_auth = args.get("api_key")
    if not ow_auth:
        return {
            "error": "API key is not set."
        }

    secret = args.get("secret")
    if not secret:
        return {
            "error": "Secret key is not set."
        }

    auth = args.get("auth")

    if secret != auth:
        return {
            "error": "Provided 'auth' secret is not valid."
        }

    with open(os.path.join(os.path.expanduser("~"), ".wskprops"), "w") as f:
        f.write("NAMESPACE={}\n".format(ow_namespace))
        f.write("AUTH={}\n".format(ow_auth))
        f.write("APIHOST={}\n".format(ow_host))

    if os.path.exists("deep-oc"):
        p = subprocess.run(
            [
                "git", "pull", "origin", "master"
            ],
            cwd="/action/deep-oc"
        )
    else:
        p = subprocess.run(
            [
                "git",
                "clone",
                "-b", "add_openwhisk_package",
                "https://github.com/deephdc/deep-oc"
            ]
        )

    tmp_env = os.environ.copy()
    tmp_env["OW_API_KEY"] = ow_auth
    tmp_env["OW_SECRET"] = ow_secret
    p = subprocess.run(
        [
            "wskdeploy",
            "sync",
            "-v",
            "-p", "deep-oc/openwhisk"
        ],
        env=tmp_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    return {
        "json": {
            "out": p.stdout.decode('ascii'),
            "err": p.stderr.decode('ascii'),
        },
        "text": (
            ">>>>>>>> STDOUT\n{}"
            ">>>>>>>> STDERR\n{}".format(
                p.stdout.decode('ascii'),
                p.stderr.decode('ascii')
            )
        )
    }
