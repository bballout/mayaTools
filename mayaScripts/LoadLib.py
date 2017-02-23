import sys
import os
import maya.mel as mel

if not 'Z:/dwtv/hub/Crew/Bill_Ballout/BelalBallout' in sys.path:
    sys.path.append('Z:/dwtv/hub/Crew/Bill_Ballout/BelalBallout')

path = 'Z:/dwtv/hub/Crew/Bill_Ballout/BelalBallout/mel/'
melFiles = os.listdir('Z:/dwtv/hub/Crew/Bill_Ballout/BelalBallout/mel')

for file in melFiles:
    mel.eval( 'source "%s%s"'%(path,file))


from scripts import UILib
reload(UILib)

try:
    toolWin.close()  # @UndefinedVariable
except:
    pass
        
toolWin = UILib.ToolBoxWin()
toolWin.show()
