TRAINDATA='/home/tre3x/python/FilmEditDetection/data/MEP_data/finaldata/train'
TESTDATA='/home/tre3x/python/FilmEditDetection/data/MEP_data/finaldata/test'
WEIGHTS='imagenet'
ENCODER='VGG16'
DIM=224
BATCH=16
EPOCH=10
STEPS=10
STEPSVAL=10
MODPATH='/home/tre3x/python/FilmEditDetection/model/hardcut/trainedmodel'


python hardcut_train.py \
--trainpath $TRAINDATA\
 --testpath $TESTDATA\
  --encoder $ENCODER\
   --weights $WEIGHTS\
    --dim $DIM\
     --batch $BATCH\
      --epoch $EPOCH\
       --steps $STEPS\
        --stepsval $STEPSVAL\
         --modpath $MODPATH