# Load env variables if needed

CAF_SS_ENV_FILE="/data/.env"
if [ -f $CAF_SS_ENV_FILE ]; then
  source $CAF_SS_ENV_FILE
fi

if [[ -z ${CAF_APP_LOG_DIR} ]]; then
  export CAF_APP_LOG_DIR="/tmp"
fi


echo "CAF_APP_LOG_DIR = ${CAF_APP_LOG_DIR}"

if [ -f /var/helloworld/helloworld ]; then
  /var/helloworld/helloworld
else
  ./helloworld
fi