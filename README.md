# MIL.testproject

This is the program to recognize text from image.
Text recognizer is based on [tesseract](https://github.com/tesseract-ocr/tesseract) ocr and [jamspell](https://github.com/bakwc/JamSpell) corrector.  

## Install

To install you must have `docker` on your computer.  

```
pip install -r requirements.txt
docker-compose pull
```

## Usage
The program processes all images from databyse.  
Start docker containers with workers, queue and db:
```
docker-compose up
```

Put your image in dir `data`. To add images in database run:
```
python text_extractor.py load
```
*Images can be re-added in database and will considered as new and unhandled.*


To process all unhandled images:
```
python text_extractor.py process
```

To clear database:
```
python text_extractor.py clear
```

## Scale test

You can change the number of workers for ocr and corrector with command:
```
docker-compose scale pytesseractocr=3
```

And
```
docker-compose scale jamspell=3
```

*3 is an example.*

### Results
Time to process dataset of 411 images:

| n ocr | n corrector | time, s |
|-------|-------------|--------:|
|  1    |     1       |    65.3 |
|  2    |     2       |    36.5 |

#### Single workers resource usage
![](report_images/single_workers.png)

#### Multiply workers resource usage
![](report_images/multiply_workers.png) 


## Examples
[Dataset description](https://rrc.cvc.uab.es/?ch=1)
[Download](https://rrc.cvc.uab.es/downloads/Challenge1_Training_Task12_Images.zip)

