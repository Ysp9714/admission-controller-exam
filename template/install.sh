source template/.env

openssl genrsa -out cert/ca.key 2048
openssl req -x509 -new -nodes -key cert/ca.key -days 100000 -out cert/ca.crt -subj "/CN=AIP Admission CA" 

cat template/server.conf | \
sed -e "s%SVCADDR%$SVCADDR%g" > cert/server.conf
openssl genrsa -out cert/server.key 2048
openssl req -new -key cert/server.key -out cert/server.csr -config cert/server.conf
openssl x509 -req -in cert/server.csr -CA cert/ca.crt -CAkey cert/ca.key -CAcreateserial -out cert/server.crt -days 100000 -extensions v3_req -extfile cert/server.conf

export CA_PEM_BASE64="$(openssl base64 -A < "cert/ca.crt")"

cat template/validatingwebhook.yaml | \
sed -e "s/CA_PEM_BASE64/$CA_PEM_BASE64/g" \
    -e "s/PODNAME/$PODNAME/g" \
    -e "s/NAMESPACE/$NAMESPACE/g" \
> src/validatingwebhook.yaml

cat template/mutatingwebhook.yaml | \
sed -e "s/CA_PEM_BASE64/$CA_PEM_BASE64/g" \
    -e "s/PODNAME/$PODNAME/g" \
    -e "s/NAMESPACE/$NAMESPACE/g" \
> src/mutatingwebhook.yaml

docker build --no-cache -f build/dockerfile . -t $ADMISSION_IMAGE_NAME:$ADMISSION_IMAGE_TAG
docker push $ADMISSION_IMAGE_NAME:$ADMISSION_IMAGE_TAG

cat template/webhook.yaml | \
sed -e s%ADMISSION_IMAGE_NAME%$ADMISSION_IMAGE_NAME%g \
    -e s%ADMISSION_IMAGE_TAG%$ADMISSION_IMAGE_TAG%g \
    -e s%NAMESPACE%$NAMESPACE%g \
    -e s%PODNAME%$PODNAME%g \
> src/webhook.yaml
