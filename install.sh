#!/bin/bash

VARCHIVE_PATH=$(dirname "$0")
cd "$VARCHIVE_PATH"

checkExist() {
    cmd="$1"
    if $cmd --help >/dev/null; then
        return 0
    fi
    return 1
}

installIfNotExist() {
    cmd="$1"
    if ! checkExist "$cmd"; then
        export HOMEBREW_NO_AUTO_UPDATE=false
        if ! brew install "$cmd"; then
            echo "Error: Cannot install $cmd" 1>&2
            exit 1
        fi
    fi
}

main() {

    cd server/pem
    ./genCA.sh
    cd -

    if ! checkExist 'brew'; then
        if /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"; then
            echo "Error: Cannot install brew" 1>&2
            exit 1
        fi
    fi
    installIfNotExist "python3"
    installIfNotExist "npm"
    installIfNotExist "ffmpeg"
    installIfNotExist "yt-dlp"

    cd server/src
    if ! python3 -m pip install -r requirements.txt; then
        echo "Error: Pythone cannot install all lib in the requirements.txt" 1>&2
        exit 1
    fi
    cd -

    cd spa
    if ! npm install; then
        echo "Error: npm install failed!" 1>&2
        exit 1
    fi
    cd -

    echo "Install successfully!"
    echo "To start varchive by running:"
    echo "$VARCHIVE_PATH/shell/varchive-start.sh"
}

main
