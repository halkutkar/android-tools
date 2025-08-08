-- DoorDash API GUI Launcher
-- This AppleScript launches the DoorDash API GUI application

tell application "Terminal"
	activate
	
	-- Get the directory where this script is located
	set scriptPath to POSIX path of (path to me)
	set scriptDir to do shell script "dirname " & quoted form of scriptPath
	
	-- Change to the scripts directory and launch the GUI
	do script "cd " & quoted form of scriptDir & " && ./launch_gui.sh"
end tell 