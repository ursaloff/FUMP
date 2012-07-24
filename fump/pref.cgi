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
$dparser::lang=\%LNG; 
is_ip_banned();
if(exists($PAR{confirm})){
	my $confirm=select_one_db("SELECT * FROM ${PREF}changepref WHERE ran=?",$PAR{confirm});
	print_error("Probably you've already confirmed your contact information modification") unless($confirm->{pk_changepref});
	my $user=select_one_db("SELECT * FROM ${PREF}user WHERE pk_user=?",$confirm->{fk_user});
	print_error("Can not find your contact information, probably you have been already removed from newsletter") unless($user->{pk_user});
	%CONF=loadCONF($user->{fk_account});
	my $page = new hfparser(
	IS_CRIPT=>0,
	DATA=>"$TempatesPrefDir/$CONF{prefpagetempl}",
	ERROR_AFTER_INPUT=>1
	);
	my $modif={name=>$confirm->{name},email=>$confirm->{email}};
	$modif->{messageformat}=$confirm->{messageformat} if $confirm->{messageformat};
	update_db("${PREF}user",$modif,{pk_user=>$user->{pk_user}});
	$db->do("DELETE FROM ${PREF}changepref WHERE pk_changepref=?",undef,$confirm->{pk_changepref});
	&Error;
	if($CONF{notify_about_modification}){
		my $mformat={0=>"default",1=>"Text",2=>"HTML",""=>"not modified"};
		$msg = new MIME::Lite 
			From    =>"FUMP<$CONF{adminemail}>",
			To      =>"$CONF{adminname} <$CONF{adminemail}>",
			Subject =>"Subscriber $user->{email} modified his contact information",
			Data    =>qq|
Account:         $ACCOUNT{$user->{fk_account}}
User ID:         $user->{pk_user}
User IP:         $ENV{REMOTE_ADDR}

Old information:
Name:            $user->{name}
Email:           $user->{email}
Messages format: $mformat->{$user->{messageformat}}
---------------
New information:
Name:            $confirm->{name}
Email:           $confirm->{email}
Messages format: $mformat->{$confirm->{messageformat}}

---------------
Powered by Follow Up Mailing List Processor PRO $VERSION
Sellwide Corp.
http://www.sellwide.com
|;
		MIMEsendto($CONF{adminemail},$msg);
	}
	$page->Hide('<!--SECOND_STEP-->');
	$page->Hide('<!--FIRST_STEP-->');
	$page->ParseData;
	my $output=$page->as_string;
	$output=PersonalizeText($output,\%CONF,$user);
	&printheader;
	print $output;
	exit;	
}
unless(length $PAR{u}){
	print_error("Incorrect request");
}
my $user=select_one_db("SELECT * FROM ${PREF}user WHERE unsubscribe=?",$PAR{u});
print_error("Sorry, but subscriber was not found") unless($user->{pk_user});
%CONF=loadCONF($user->{fk_account});
my $page = new hfparser(
	IS_CRIPT=>0,
	DATA=>"$TempatesPrefDir/$CONF{prefpagetempl}",
	ERROR_AFTER_INPUT=>1
);
if($CONF{disable_modify}){
	print_error($LNG{ERROR_NOT_ALLOWED_TO_MODIFY});
}
unless($CONF{confirm_modify_subject}){
	print_error($LNG{ERROR_CONFIRM_SUBJ_NOT_DEFINED});
}
unless($CONF{confirm_modify_body}){
	print_error($LNG{ERROR_CONFIRM_BODY_NOT_DEFINED});
}
if($PAR{mode} eq 'thankyou'){
		&printheader;
		$page->Hide('<!--FIRST_STEP-->');
		$page->Hide('<!--THIRD_STEP-->');
		$page->add_regesp('{email}',$PAR{email});
		$page->ParseData;
		my $output=$page->as_string;
		$output=PersonalizeText($output,\%CONF,$user);
		print $output;
		exit;
}
if($PAR{issubmit}){
	map{$page->set_error($_,$LNG{ERROR_REQUIRED}) unless length($PAR{$_})}qw(name email);
	unless($page->is_error){
		$page->set_error('email',$LNG{ERROR_EMAIL_INCORRECT}) unless checkemail($PAR{email});
	}
	unless($page->is_error){
		my @chars=('a'..'z','A'..'Z',0..9);
		my $ran=join("", @chars[map{rand @chars}(1..15)]);
		my $messformat=0;
		$messformat=$PAR{messageformat} if exists($PAR{messageformat});
		my $sql=qq|INSERT INTO ${PREF}changepref (fk_user, ran , name, email, messageformat, date, ip) VALUES (?,?,?,?,?,$NOW,?)|;
		$db->do($sql,undef,$user->{pk_user},$ran,$PAR{name},$PAR{email},$messformat,$ENV{REMOTE_ADDR});
		&Error;
		$messsubj=$CONF{confirm_modify_subject};
		$messbody=$CONF{confirm_modify_body};
		my $confirm_url="$CONF{serverurl}pref.cgi?confirm=$ran";
		$messbody=~s/\[CONFIRM_URL\]/$confirm_url/;
		$messbody=PersonalizeText($messbody,\%CONF,$user);
		$messsubj=PersonalizeText($messsubj,\%CONF,$user);
		$msg = new MIME::Lite 
			From    =>"$CONF{fromname} <$CONF{fromemail}>",
			To      =>"$PAR{name} <$PAR{email}>",
			Subject =>$messsubj,
			Data    =>$messbody;
		MIMEsendto($PAR{email},$msg);
		print $q->redirect("$ENV{SCRIPT_NAME}?u=$PAR{u}&mode=thankyou&email=$PAR{email}");
		exit;
	}
}
&printheader;
unless($CONF{allow_modyfy_format}){
	$page->Hide('<!--ALLOWCHANGEFORMAT-->');
}
map{$page->set_def($_,$user->{$_})}qw(name email messageformat);
map{$page->set_input($_,{size=>30})}qw(name email);
$page->add_element('messageformat',1,$LNG{TEXT_ONLY});
$page->add_element('messageformat',2,$LNG{HTML_ONLY});
$page->Hide('<!--SECOND_STEP-->');
$page->Hide('<!--THIRD_STEP-->');
$page->ParseData;
my $output=$page->as_string;
$output=PersonalizeText($output,\%CONF,$user);
print $output;

sub print_error{
	my $mess=shift;
	printheader();
	print $q->start_html($mess);
	print qq|<h1 align="center"><font color="red">$mess</font></h1>|;
	print $q->end_html();
	exit();
}
