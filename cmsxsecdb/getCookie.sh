
COOKIEDIR=~/.private/
mkdir $COOKIEDIR

env -i KRB5CCNAME="$KRB5CCNAME" cern-get-sso-cookie -u https://cms-gen-dev.cern.ch/xsdb -o ${COOKIEDIR}/xsdbdev-cookie.txt --krb -r
