#!/bin/bash

WORKDIR=$(pwd)
FUNCTIONS=("$@");
if [ $# -eq 0 ]; then
    FUNCTIONS=('convertToAudio' 'getArticle' 'newArticle' 'newArticle_html');
fi

start=`date +%s`
for FUNCTION in ${FUNCTIONS[@]}
do
  echo 'UPDATING' $FUNCTION
  cd $FUNCTION/src/
  zip -r $WORKDIR/code.zip * > /dev/null
  cd ../packages
  zip -ur $WORKDIR/code.zip * > /dev/null
  cd ../venv/lib/python2.7/site-packages
  zip -ur $WORKDIR/code.zip * > /dev/null
  cd $WORKDIR
  aws lambda update-function-code --function-name $FUNCTION --zip-file fileb://code.zip
  rm code.zip
done

end=`date +%s`
runtime=$((end-start))
echo 'RUNTIME:' $runtime 'seconds'

