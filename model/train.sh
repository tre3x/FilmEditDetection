TRAINDATA='core/data/train'
TESTDATA='core/data/test'
SDCNN=3
DDCNN=4
F=16
BATCH=32
EPOCH=60
STEPS=40
STEPSVAL=40
MODPATH='core/trainedmodel'


python softcut_train.py \
--trainpath $TRAINDATA\
 --testpath $TESTDATA\
  --sdcnn $SDCNN\
   --ddcnn $DDCNN\
    --f $F\
     --batch $BATCH\
      --epoch $EPOCH\
       --steps $STEPS\
        --stepsval $STEPSVAL\
         --modpath $MODPATH