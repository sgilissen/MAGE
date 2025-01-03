# MAGE
MAGE - Management and Administration for Game Environments

![MAGE server view (frontend)](/MAGE-screenshot.png?raw=true "MAGE server view (frontend)")

MAGE is a Django-based gameserver manager. 
It queries gameservers to display the current in-game statistics. 
While it's still very much work in progress (and probably forever will be, seeing as there are constantly new games being added), it has been used in several game tournaments already. 

Currently supported games: 
- Unreal Tournament (UT99)
- Unreal Tournament 2003
- Unreal Tournament 2004
- Quake 3 Arena (and Q3A-based games)

More will be implemented later.

Technology used: 
- Django
- Redis
- Tailwind
- Custom scripting for querying gameservers
