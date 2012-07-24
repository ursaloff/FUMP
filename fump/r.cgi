#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 08/29/2006                                           #
######################################################################
use lib('lib');
require 'conf.cgi';
%CONF=(); %PAR=();%ACCOUNT=();
$q=new CGI;
&par_prepare;
&db_prepare;
is_ip_banned();
my $link=select_one_db("SELECT * FROM ${PREF}links WHERE pk_link=?",$PAR{l});
unless ($link->{pk_link}){
	my $page=new hfparser
		IS_CRIPT=>0,
		DATA=>"shabl/linknotfound.html",
		ERROR=>\%error
	;
	$page->add_regesp('{VERSION}',$CONF{VERSION});
	$page->ParseData;
	$page->print;
	exit(1);
}
my $user=select_one_db("SELECT * FROM ${PREF}user WHERE unsubscribe=?",$PAR{u});
my $mess=select_one_db("SELECT * FROM ${PREF}mess WHERE pk_mess=?",$PAR{m});
my $sql=qq|INSERT INTO ${PREF}link_clicks (fk_user,fk_link, fk_mess, timestamp)
VALUES (?,?,?,$NOW)|;
$db->do($sql,undef,$user->{pk_user},$link->{pk_link},$mess->{pk_mess});
Error($sql);
print $q->redirect($link->{redirect_link});
exit;

