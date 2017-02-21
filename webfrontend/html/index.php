<?php
// LoxBerry KNXd-Plugin 
// Christian Woerstenfeld - git@loxberry.woerstenfeld.de
// Version 1.7
// 21.02.2017 22:16:36

// Configuration parameters
$psubdir          =array_pop(array_filter(explode('/',pathinfo($_SERVER["SCRIPT_FILENAME"],PATHINFO_DIRNAME))));
$mydir            =pathinfo($_SERVER["SCRIPT_FILENAME"],PATHINFO_DIRNAME);
$logfile 					=$mydir."/../../../../log/plugins/$psubdir/knxd.log";
$gad_query_script =$mydir."/../../../cgi/plugins/$psubdir/bin/gad_query.pl";
$user 						="KNXd";
$pass 						="loxberry";

// Enable logging
ini_set("error_log", $logfile);
ini_set("log_errors", 1);

function authenticate()
{
		header("WWW-Authenticate: Basic realm='LoxBerry - KNXd-Plugin'");
    header("HTTP/1.0 401 Unauthorized");
		return "\nError, Access denied.\n";
}

// Defaults for inexistent variables
if (!isset($_REQUEST["mode"])) {$_REQUEST["mode"] = 'normal';}

if ($_REQUEST["mode"] == "read_bus")
{
				$result = "\n".shell_exec('echo "Reading KNX Telegrams for max. 10 seconds from now:";(sleep 10;pkill knxtool)& (CNT=1; knxtool groupsocketlisten ip: | while read LINE; do printf "%02d" $CNT;  echo " = $LINE";  CNT=$(( $CNT + 1 )); done)');
				#if [ $CNT -gt 10 ]; then pkill knxtool; fi; 
				error_log( date('Y-m-d H:i:s ')."[READ_BUS] $result \n", 3, $logfile);
}
else if ($_REQUEST["mode"] == "gad_query")
{
	if (file_exists($gad_query_script)) 
	{
		if( ( isset($_SERVER['PHP_AUTH_USER'] ) && ( $_SERVER['PHP_AUTH_USER'] == "$user" ) ) AND  ( isset($_SERVER['PHP_AUTH_PW'] ) && ( $_SERVER['PHP_AUTH_PW'] == "$pass" )) )
		{
				$result = "\n".shell_exec("$gad_query_script");
				error_log( date('Y-m-d H:i:s ')."[GAD-Query] OK \n", 3, $logfile);
		}
		else
		{
				$result = authenticate();
		}
	}
	else
	{
		error_log( date('Y-m-d H:i:s ')."[GAD-Query] Error, Script missing \n", 3, $logfile);
		$result = "Error, gad_query-Script missing \n";
	}
}
else if($_REQUEST["mode"] == "download_logfile")
{
	if (file_exists($logfile)) 
	{
		error_log( date('Y-m-d H:i:s ')."[LOG] Download logfile\n", 3, $logfile);
    header('Content-Description: File Transfer');
    header('Content-Type: text/plain');
    header('Content-Disposition: attachment; filename="'.basename($logfile).'"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($logfile));
    readfile($logfile);
	}
	else
	{
		error_log( date('Y-m-d H:i:s ')."Error reading logfile!\n", 3, $logfile);
		die("Error reading logfile."); 
	}
	exit;
}
else if($_REQUEST["mode"] == "show_logfile")
{
	if (file_exists($logfile)) 
	{
		error_log( date('Y-m-d H:i:s ')."[LOG] Show logfile\n", 3, $logfile);
    header('Content-Description: File Transfer');
    header('Content-Type: text/plain');
    header('Content-Disposition: inline; filename="'.basename($logfile).'"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($logfile));
    readfile($logfile);
	}
	else
	{
		error_log( date('Y-m-d H:i:s ')."Error reading logfile!\n", 3, $logfile);
		die("Error reading logfile."); 
	}
	exit;
}
else if($_REQUEST["mode"] == "empty_logfile")
{
	if (file_exists($logfile)) 
	{
		if( ( isset($_SERVER['PHP_AUTH_USER'] ) && ( $_SERVER['PHP_AUTH_USER'] == "$user" ) ) AND  ( isset($_SERVER['PHP_AUTH_PW'] ) && ( $_SERVER['PHP_AUTH_PW'] == "$pass" )) )
		{
				$f = @fopen("$logfile", "r+");
				if ($f !== false) 
				{
				    ftruncate($f, 0);
				    fclose($f);
						error_log( date('Y-m-d H:i:s ')."[LOG] Logfile content deleted\n", 3, $logfile);
						$result = "\n<img src='/plugins/$psubdir/KNXD_STATUS_0.png'>";
				}
				else
				{
						error_log( date('Y-m-d H:i:s ')."[LOG] Logfile content not deleted due to problems doing it.\n", 3, $logfile);
						$result = "\n<img src='/plugins/$psubdir/KNXD_STATUS_DOWN.png'>";
				}
		}
		else
		{
				$result = authenticate();
		}
	}
	else
	{
		$result = "\n<img src='/plugins/$psubdir/KNXD_STATUS_DOWN.png'>";
	}
}
else
{
		$result = "Error, invalid request \n Try: ?mode=gad_query";
}

header('Content-Type: text/plain; charset=utf-8');
echo "$result";
exit;
