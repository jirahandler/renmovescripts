#!/bin/bash

input_pdf="QNSPAP.pdf"
output_prefix="QNSPAP"
max_pages=150
total_pages=$(pdftk "$input_pdf" dump_data | grep NumberOfPages | awk '{print $2}')

current_page=1
part=1

while [ $current_page -le $total_pages ]; do
    end_page=$((current_page + max_pages - 1))
    if [ $end_page -gt $total_pages ]; then
        end_page=$total_pages
    fi
    output_pdf="${output_prefix}_${part}.pdf"
    pdftk "$input_pdf" cat $current_page-$end_page output "$output_pdf"
    current_page=$((end_page + 1))
    part=$((part + 1))
done

echo "PDF has been split into parts with a maximum of $max_pages pages each."
