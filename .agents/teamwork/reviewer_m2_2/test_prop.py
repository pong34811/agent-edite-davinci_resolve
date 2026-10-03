import sys, os
os.environ['RESOLVE_SCRIPT_LIB'] = r'C:\Program Files\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
sys.path.append(r'C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\lib\modules')
import DaVinciResolveScript as dvr

r = dvr.scriptapp('Resolve')
p = r.GetProjectManager().GetCurrentProject()
for i in range(1, p.GetTimelineCount()+1):
    tl = p.GetTimelineByIndex(i)
    if tl.GetName() == 'หนีฝ่าความหนาว_Minecraft-vdo_9x16':
        it1 = tl.GetItemListInTrack('video', 1)[0]
        print('V1 it.GetProperty("Tilt"):', repr(it1.GetProperty('Tilt')))
        print('V1 it.GetProperty()["Tilt"]:', repr(it1.GetProperty().get('Tilt')))
        print('V1 it.GetProperty("CropBottom"):', repr(it1.GetProperty('CropBottom')))
        print('V1 it.GetProperty()["CropBottom"]:', repr(it1.GetProperty().get('CropBottom')))
        
        it2 = tl.GetItemListInTrack('video', 2)[0]
        print('V2 it.GetProperty("Pan"):', repr(it2.GetProperty('Pan')))
        print('V2 it.GetProperty()["Pan"]:', repr(it2.GetProperty().get('Pan')))
        print('V2 it.GetProperty("Tilt"):', repr(it2.GetProperty('Tilt')))
        print('V2 it.GetProperty()["Tilt"]:', repr(it2.GetProperty().get('Tilt')))
        print('V2 it.GetProperty("CropTop"):', repr(it2.GetProperty('CropTop')))
        print('V2 it.GetProperty()["CropTop"]:', repr(it2.GetProperty().get('CropTop')))
