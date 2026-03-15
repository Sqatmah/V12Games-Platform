@echo off
cd C:\Users\sqatm\Desktop\V12Games
call venv\Scripts\activate
python manage.py sync_new_games --count 15 --days 7
echo Done! %date% %time%




#أمر اضافة اخر 7 ايام 
