#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 08/29/2006                                           #
######################################################################
use lib('lib');
use CGI::Carp qw(fatalsToBrowser);
use CGI;
$q=new CGI;
unless ($^O=~/win/i){
	my $child=fork();
	die "Can not fork: $!" unless defined $child;
	if ($child==0){
		exec("$^X broadcaster");
	}
	print $q->header("image/gif");
	map{print chr($_)}qw(71 73 70 56 57 97 2 0 2 0 128 1 0 153 153 153 255 255 255 33 249 4 1 0 0 1 0 44 0 0 0 0 2 0 2 0 0 2 2 140 83 0 59);
}else{
	print $q->header("image/gif");
	map{print chr($_)}qw(71 73 70 56 57 97 2 0 2 0 128 1 0 153 153 153 255 255 255 33 249 4 1 0 0 1 0 44 0 0 0 0 2 0 2 0 0 2 2 140 83 0 59);
	exec("$^X broadcaster");
}
