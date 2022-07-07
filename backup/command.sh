# copies ssl certificates
mkdir -p certs
cp ../gen-certs/{ca-cert.pem,server-cert.pem,server-key.pem} $CERTS_DIR/