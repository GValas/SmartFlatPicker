#!/usr/bin/env bash
#!/usr/bin/env bash
DIR="$( cd "$( dirname "$0" )" && pwd )"
python3 ${DIR}/SeLogerComScrapper.py LOCALHOST 27017 ${DIR}/log/log.txt