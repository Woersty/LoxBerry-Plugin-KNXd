#!/usr/bin/perl
# 
# Version 1.0
# LoxBerry KNXd Plugin Control Server
#
use IO::Socket::INET;
 
# auto-flush on socket
$| = 1;
 
# creating a listening socket
my $socket = new IO::Socket::INET (
    LocalHost => '0.0.0.0',
    LocalPort => '5679',
    Proto => 'tcp',
    Listen => 5,
    Reuse => 1
);
die "cannot create socket $!\n" unless $socket;
print "KNXd control server waiting for client connection on port 5679\n";
 
while(1)
{
    # waiting for a new client connection
    my $client_socket = $socket->accept();
 
    # get information about a newly connected client
    my $client_address = $client_socket->peerhost();
    my $client_port = $client_socket->peerport();
 
    # read up to 1024 characters from the connected client
    my $data = "";
    $client_socket->recv($data, 1024);
    #print "received data: $data\n";

    if ( "$data" eq "ReStArT_KnXd" )
    {
    	system("REPLACEBYBASEFOLDER/system/daemons/plugins/REPLACEBYPLUGINNAME");
			  if ($? ne 0) 
			  {
			    $data = "TXT_ERROR2_CONFIG_SAVED";
			  } 
			  else 
			  {
			    $data = "TXT_OK_CONFIG_SAVED";
			  }
    }
    elsif ( "$data" eq "StAtUs_KnXd" )
    {
	    	system("service knxd status 2>&1 >/dev/null");
		    $data = "KNXD_STATUS_".$?;
    }
    else
    {
    	    $data = "TXT_ERROR3_CONFIG_SAVED";
    }
    $client_socket->send($data);
 
    # notify client that response has been sent
    shutdown($client_socket, 1);
}
 
$socket->close();
