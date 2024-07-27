for f1 in *.pdf; do
  for f2 in *.pdf; do
    if [ "$f1" != "$f2" ]; then
      diff-pdf --output-diff=diff.pdf "$f1" "$f2" > /dev/null 2>&1
      if [ $? -eq 0 ]; then
        echo "$f1 and $f2 are identical"
        if [[ $f1 =~ _7013\.pdf$ || $f2 =~ _7013\.pdf$ ]]; then
          if [[ $f1 =~ _7013\.pdf$ && $f2 =~ _7013\.pdf$ ]]; then
            echo "Both files end with _7013.pdf. Please choose one to delete."
            read -p "Delete $f1? (y/n): " answer
            if [ "$answer" = "y" ]; then
              rm "$f1"
              echo "$f1 has been deleted"
            else
              read -p "Delete $f2? (y/n): " answer
              if [ "$answer" = "y" ]; then
                rm "$f2"
                echo "$f2 has been deleted"
              fi
            fi
          elif [[ $f1 =~ _7013\.pdf$ ]]; then
            read -p "$f2 does not end with _7013.pdf. Delete $f2? (y/n): " answer
            if [ "$answer" = "y" ]; then
              rm "$f2"
              echo "$f2 has been deleted"
            fi
          elif [[ $f2 =~ _7013\.pdf$ ]]; then
            read -p "$f1 does not end with _7013.pdf. Delete $f1? (y/n): " answer
            if [ "$answer" = "y" ]; then
              rm "$f1"
              echo "$f1 has been deleted"
            fi
          fi
        else
          echo "Both files do not end with _7013.pdf. Please choose one to delete."
          read -p "Delete $f1? (y/n): " answer
          if [ "$answer" = "y" ]; then
            rm "$f1"
            echo "$f1 has been deleted"
          else
            read -p "Delete $f2? (y/n): " answer
            if [ "$answer" = "y" ]; then
              rm "$f2"
              echo "$f2 has been deleted"
            fi
          fi
        fi
      fi
    fi
  done
done
