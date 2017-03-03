#!/bin/bash

book_name=$1
catss_file=$2
book_num=$3

python3 ~/software/biblical-studies/catss/starter.py $catss_file > $book_name-catss.txt
python3 convert-swete.py -v 3 -c $book_num compare > $book_name-swete.txt
diff -y $book_name-catss.txt $book_name-swete.txt > $book_name.txt
