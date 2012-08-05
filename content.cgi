#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 08/29/2006                                           #
######################################################################
use CGI;
$q=new CGI;
my %PAR=();
map{$PAR{$_}=$q->param($_)}$q->param();


if($PAR{get} eq 'calendar' or $PAR{get} eq 'selectbox' or $PAR{get} eq 'htmltotext'){
	open(FILE,"shabl/$PAR{get}.js");
	print $q->header('text/plain');
	while(<FILE>){print};
	close(FILE);
	exit;
}
if($PAR{get} eq 'css'){
	open(FILE,"shabl/style.css");
	print $q->header('text/plain');
	while(<FILE>){print};
	close(FILE);
	exit;
}
if($PAR{get} eq 'image' and -f "shabl/img/$PAR{f}.$PAR{mode}"){
	open (FILE,"shabl/img/$PAR{f}.$PAR{mode}");
	binmode(FILE);
	print $q->header('image/'.$PAR{mode});
	while(<FILE>){print};
	close(FILE);
	exit;
}
