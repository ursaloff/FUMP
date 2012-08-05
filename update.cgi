#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 08/29/2006                                           #
######################################################################
use lib('lib');
require 'conf.cgi';
&par_prepare;
$shabl_page_install="$SHABL_DIR/upgrade.html";
local %func;
#local @tables=sort {$a cmp $b} qw(account attach conf doi doiaccounts doppar fields log mess ses tosend user);
%func=(1=>1, 2=>1,3=>1);
&db_prepare;
@UPDATE=LoadUpdateStructure();
&print_all;
sub print_all{
	&printheader;
	$PAR{step}=1 unless $PAR{step};
	my $page=new hfparser(
		DATA=>$shabl_page_install
	);
	$page->SplitData("<!--START-->","<!--END-->");
	my $what;
	$what = &print_step2 if exists $func{$PAR{step}};
	$what = "<h1 class=\"mess\">Do not change the URL!!!</h1>" unless exists $func{$PAR{step}};
	$page->replaceINSIDE($what);
	$page->add_regesp('###VERSION###',$VERSION);
	$page->ParseData;
	$page->print;
}
sub print_step2{
	if ($PAR{step}>2){
		return &print_step3;
	}
	my $page=new hfparser(
		DATA=>$shabl_page_install,
		ERROR_AFTER_INPUT=>0
	);
	$page->SplitData("<!--START2-->","<!--END2-->");
	$page->deleteBEFORE_AFTER();
	my $mess;
	unless (defined($db)){
		$mess="<H1 class=mess>Error: could not connect to your previous database. Probably you must reinstall database: please run install.cgi script!</H1>"
	}else{
		my @UPG=();
		map{
			if(defined($_->{c})){
				push (@UPG, $_) if &{$_->{c}};
			}
		}@UPDATE;
		unless(@UPG){
			$mess=qq|<h1 class="mess">No upgrade required</h1>  <h1 class="mess">To start work please <a href="responder.cgi">Click here&gt;&gt;&gt;</a></h1>|;
			$page->Hide('<!--UPG-->','<!--UPG-->');
		}else{
			$mess=qq|<table width=90% border=0 align=center>
				<TR align="center">
				<TD width=10%><B>Version</B></TD>
				<TD width=90% ><B>Action</B></TD>
				<!--<TD width=55%><B>SQL</B></TD>-->
			</TR>
			|;
			map{
			$mess.=qq|
				<TR align="center">
				<TD width=10%><B>$_->{v}</B></TD>
				<TD width=90% align=left>$_->{n}</TD>
				<!--<TD width=55%>$_->{q}</TD>-->
			</TR>
			|;			
			}@UPG;			
			$mess.=qq|</table>|;
		}
	}

	
	$page->add_regesp('{message}',$mess);
	$page->ParseData;
	return $page->as_string;
}
########################
sub print_step3{
	my $page=new hfparser(
		DATA=>$shabl_page_install,
	);
	local $isexists=0;
	my @UPG=();
	map{
		if(defined($_->{c})){
			
			if (&{$_->{c}}){
				if($_->{q}){
					$db->do($_->{q});
				}
				if(defined($_->{s})){
					&{$_->{s}};
				}
				if ($DBI::err){
					$_->{st}="<font color=red>$DBI::errstr</font>";
				}else{
					$_->{st}="<font color=green><B>OK</B></font>";
				}
				push (@UPG, $_);
			}
			
		}
	}@UPDATE;
	$page->SplitData("<!--START3-->","<!--END3-->");
	my $mess;
	unless(@UPG){
		$mess="<h1 class=mess>No instructions</h1>";
	}else{
		$mess=qq|<table width=90% border="0" align="center">
			<TR align="center">
			<TD width=10%><B>Version</B></TD>
			<TD width=45% ><B>Action</B></TD>
			<TD width=45%><B>Status</B></TD>
		</TR>
		|;
		map{
		$mess.=qq|
			<TR align="center">
			<TD width=10%><B>$_->{v}</B></TD>
			<TD width=45% align=left>$_->{n}</TD>
			<TD width=45%>$_->{st}</TD>
		</TR>
		|;			
		}@UPG;			
		$mess.=qq|</table>|;
	}
	save_config(0,'VERSION',$VERSION);
	$page->add_regesp('{message}',$mess);
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
