# MIL.testproject

This is the program to recognize text from image.
Text recognizer is based on [tesseract](https://github.com/tesseract-ocr/tesseract) ocr and [jamspell](https://github.com/bakwc/JamSpell) corrector.  

## Install

To install you must have `docker` on your computer.  

```
pip install -r requirments.txt
docker-compose run
```

## Usage
The program processes all images from databyse.  
Start docker containers with workers and db:
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

## Scale test

You can change the number of workers for ocr and corrector with command:
```
docker-compose scale pytesseractocr=3
```

And
```
docker-compose scale jamspell=3
```

*3 is an example*
