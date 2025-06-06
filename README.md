# cod-modern-warfare-launcher
Launcher made in python to launch different versions of Call of Duty Modern Warfare while also managing their save data to ensure they dont conflict

![image](https://github.com/user-attachments/assets/47f5bcde-577c-4e2f-8c11-dd055d7e268b)

# USAGE

1. Open ``config.json`` and set all paths accordingly for your system. (Use my template from that file). Remove entries you don't want.
2. Make sure the path you set at ``backup`` already exists to avoid issues.
3. ``save`` should always point at your Documents\Call of Duty Modern Warfare. (it may cause issues if you do not use onedrive backup for your Documents folder. havent tried.)
4. Open ``steam.json`` and set your Steam ID to see your achievements and for some personalization, or leave blank.
5. Open the launcher, and then launch one of the versions.
6. Use settings exclusive to the 1.20 version.

# HOW IT WORKS

Before launching a version of the game, the launcher will copy the contents of the ``backup`` path to ``save``, to ensure that the data of the appropriate version is used. Once it launches the game's executable, it will hang until you finish playing. Then, it will copy the contents of ``save`` into the ``backup`` folder of the version you launched. and ``save`` will then be deleted to avoid causing issues with other versions of the game.

# BUILD FROM SOURCE

Open Command Prompt at the path of the source and run ``pip install -r requirements.txt``

Then use the included ``build.bat``

# Contribute

Found a bug or want to help improve the launcher? Make an **Issue** or **Pull Request**! 


