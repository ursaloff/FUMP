#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 08/29/2006                                           #
######################################################################
use lib('lib');
use CGI;
use hfparser;
use dparser;
use repparser;
use CGI::Carp qw(fatalsToBrowser);
require "func.cgi";
local %PAR;
$q=new CGI;
#Session idle interval in minutes
$SESSION_INTERVAL=50;
$SHABL_DIR="shabl";
$SCRIPT_NAME="http://$ENV{HTTP_HOST}$ENV{SCRIPT_NAME}";
$main_shabl="$SHABL_DIR/account_shabl.html";
$settings_shabl="$SHABL_DIR/settings_shabl.html";
$links_shabl="$SHABL_DIR/links.html";
$HTMLEditorURL="/xinha/";
$glbackupdir="backup";
#open (F,"$SHABL_DIR/style.css")||die "can not read  $SHABL_DIR/style.css file";
#my $css;
#while (<F>){$css.=$_}
$dparser::GlobalRegesps={
	'{ME}'=>$SCRIPT_NAME,
#	'{CSS}'=>$css,
	'{YEAR_NOW}'=>$YEAR_NOW,
	'{VERSION}'=>$VERSION
};
###############################
sub par_prepare{
	#uploading files problem was there :(
	#$q=new CGI;
	hfparser::setCGI($q);
	my @pars=$q->param();
	foreach (@pars){$PAR{$_}=$q->param($_)}
	#$dparser::GlobalRegesps->{"{ses}"}=$PAR{ses};
	map{$dparser::GlobalRegesps->{"{$_}"}=$PAR{$_} }keys %PAR;
}
sub printpar{
	printheader();
	foreach (keys %PAR){
		print "$_ = '$PAR{$_}'<BR>";
	}
}
#############
sub printconf{
foreach (keys %CONF){
print "\$CONF{$_}=\"$CONF{$_}\"<BR>\n";
}

}
###############################
sub printheader{
	unless($CONF{defcharset}){
		print $q->header;
	}else{
		print $q->header( -charset=>$CONF{defcharset});
	}
}
###############################
sub redirect_to_login{
	my $dir=$ENV{SCRIPT_NAME};
	return if $dir=~/responder\./;
	$dir=~s/[^\\\/]*?$//;
	print $q->redirect("http://$ENV{HTTP_HOST}$dir"."responder.cgi");
	exit;
}
###############################
sub sessiya{
	my %error;
	$dparser::GlobalRegesps->{'<!--CHARSET-->'}=get_meta_charset();
	

	if (exists($PAR{pwd})){
		if($PAR{pwd} eq $CONF{adminpwd}){
			my $page=new hfparser
					DATA=>"shabl/author.html",
			;
			my $sql="INSERT INTO ${PREF}ses  (ran, host,date) VALUES (?,?,$NOW)";
			my $out=$db->prepare($sql);
			my @chars=('a'..'z','A'..'Z',0..9,'_');
			my $ran=join("", @chars[map{rand @chars}(1..25)]);
			$out->execute($ran,$ENV{REMOTE_ADDR});
			&Error;
			print $q->redirect("$SCRIPT_NAME?ses=$ran");
			if($db->do("DELETE FROM ${PREF}ses WHERE date<date_sub($NOW ,interval 2 day)")){
				$db->do("OPTIMIZE TABLE ${PREF}ses");
			}
			exit(1);
		}else{
			$error{pwd}="Incorrect password";
		}
	}
	if(exists($PAR{ses})){
		my $sql="SELECT * FROM  ${PREF}ses  WHERE (ran=?) AND (date>date_sub($NOW ,interval $SESSION_INTERVAL minute))";
		my $out=$db->prepare($sql);
		$out->execute($PAR{ses});
		&Error;
		if ($out->rows > 0){
			my $id=0;
			my  %output=%{$out->fetchrow_hashref};
			$id=$output{pk_ses};
			$db->do("UPDATE ${PREF}ses SET date=$NOW WHERE pk_ses='$id'");
			&Error;
			return 1;
		}
		
	}
	&redirect_to_login;
	&printheader;
	my $page=new hfparser
		DATA=>"shabl/author.html",
		ERROR=>\%error
	;
	$page->add_regesp('{VERSION}',$VERSION);
	$page->ParseData;
	$page->print;
	exit(1);

}
sub get_hor_menu{
	my $ref_menu=shift;
	my $ref_def_pars=shift;
	my $ref_links_classes=shift;
	#my $add_params=shift;
	my $level=shift;
	$level++;
	my @MENU=@{$ref_menu};
	my $out;
	$out=$q->start_table({-border=>0,-align=>"center",width=>"100%"})."<TR>";
	my $count=@MENU;
	my $width=int(100/$count)."%" if $count;
	my $menu;
	my $add_account;
	foreach my $element(@MENU){
		my %params=%{$ref_def_pars};
		my @params;
		my $add_params=$element->{add_params};
		map{$params{$_}=$element->{params}{$_}}keys %{$element->{params}};
		map { push(@params,"$_=$params{$_}")}keys %params;
		map { 
			push(
				@params,"$_=".$q->escape($PAR{$_}) 
			    )} @{$add_params};
		#my @classes=@{$ref_links_classes};
		my $isnow=1;
		my $class_now;
		map{ $isnow=0 unless($params{$_} eq $PAR{$_}) }keys %params;
		if ($isnow){
			$class_now=$ref_links_classes->[$level-1][1];
		}else{
			$class_now=$ref_links_classes->[$level-1][0];
		}
		$out.=$q->td({-align=>'center', -width=>$width},
				$q->a({-href=>"$SCRIPT_NAME?".join('&',@params),-target=>'_self', -class=>"$class_now"},"<NOBR>$element->{name}</NOBR>")
			)."\n";
		if ($isnow){
			if (exists=>$element->{nextlevel}){
				$add_account=get_hor_menu($element->{nextlevel},\%params,$ref_links_classes,$level);	
			}
		}
	}
	$out.="</TR>".$q->end_table().$add_account ;
	return $out;	
}
##############################
1;
