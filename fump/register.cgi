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
if ($PAR{unsubscribe} || $PAR{un}){
	unsubscribe();
	exit;
}
if($PAR{act} eq 'thankyou'){
	print_thank_you_page();
}
if($PAR{act} eq 'pleaseconfirm'){
	print_confirm_page();
}
if($PAR{act} eq 'm'){
	##One click subscribe
	my $account_id=$PAR{list};
	my $user_run=$PAR{'sub'};
	print_error($LNG{REG_ACCOUNT_WAS_NOT_FOUND}) unless($account_id);
	print_error($LNG{REG_ACCOUNT_WAS_NOT_FOUND}) unless(exists $ACCOUNT{$account_id});
	print_error($LNG{REG_SUBSCRIBER_WAS_NOT_FOUND}) unless($user_run);
	my $user=select_one_db("SELECT * FROM ${PREF}user WHERE unsubscribe=?",$user_run);
	print_error($LNG{REG_SUBSCRIBER_WAS_NOT_FOUND}) unless($user->{pk_user});
	my %CONF=loadCONF($account_id);
	print_error("$LNG{REG_REDIRECT_LINK_NOT_FOUND} $ACCOUNT{$account_id}") unless($CONF{redirsub});
	my $user=&registerUSER($account_id,$user->{email},$user->{name},undef,undef,$user->{messageformat});
	my $ran=create_unsubscribe_link($user);
	if($CONF{isdoi}){
		#double opt in
		if ($CONF{personalizeddoi}){			
			print $q->redirect($ENV{SCRIPT_NAME}."?act=pleaseconfirm&subscriber=$ran");
		}else{
			print $q->redirect($CONF{doiconfurl});
		}
	}else{
		#normal subscribe
		if ($CONF{personalizedsub}){			
			print $q->redirect($ENV{SCRIPT_NAME}."?act=thankyou&subscriber=$ran");
		}else{
			print $q->redirect($CONF{redirsub});
		}			
	}

#	if ($CONF{personalizedsub}){
#		my $ran=create_unsubscribe_link($user);
#		print $q->redirect($ENV{SCRIPT_NAME}."?act=thankyou&subscriber=$ran");
#	}else{
#		print $q->redirect($CONF{redirsub});
#	}
	exit(1);	
}
if ($PAR{act}){
	#confirm
	confirm();
	exit;
}
unless(exists $ACCOUNT{$PAR{account}}){
	print_error("$LNG{REG_ACCOUNT_IS_NOT_EXIST}");
}
local @FIELDS;
@FIELDS=load_account_fields($PAR{account});
my %DopParams,%Fields_names;
foreach(@FIELDS){
	my $param="dp".$_->{key};
	$DopParams{$_->{key}}=$PAR{$param};
	$Fields_names{$_->{key}}=$_->{name};
}
my $page = new hfparser(
	IS_CRIPT=>0,
	DATA=>"$SHABL_DIR/regerror.html",
	ERROR_AFTER_INPUT=>1
);
if ($PAR{account}){
	$page->set_error("email","$LNG{REG_EMAIL_IS_INCORRECT}") unless checkemail($PAR{email});
	unless($page->is_error){
		if($CONF{useblacklist}){
			$page->set_error("email",$CONF{blacklist_error}) if GetSQLCount("SELECT * FROM ${PREF}bounce_banemails WHERE email=?",$PAR{email});
		}
  	}  
	$page->set_error("name","$LNG{REG_REQUIRED}") if (length($PAR{name})<1);
	$page->set_error("name","$LNG{ERROR_INCORRECT}") if ($PAR{name}=~/[<>;,\\%^#]/);
	$page->set_error("email",$CONF{banmailserror}) if (is_email_banned($PAR{email},$CONF{banmails}));
	foreach(@FIELDS){
		next unless $_->{is_req};
		my $param="dp".$_->{key};
		$page->set_error($param,"$LNG{REG_REQUIRED}") if  (length($PAR{$param})<1);
	}
	unless($page->is_error){
		if(GetSQLCount("SELECT * FROM ${PREF}user WHERE fk_account=? AND email=?",$PAR{account},$PAR{email})){
			if(length($CONF{alreadysub})>7 and check_url($CONF{alreadysub})){
				print $q->redirect($CONF{alreadysub});
				exit;
			}			
		}
		my @optional_subscribe=$q->param('optional_subscribe');
		my $user=&registerUSER($PAR{account},$PAR{email},$PAR{name},\%DopParams,\%Fields_names,$PAR{messageformat},\@optional_subscribe,$PAR{fromname},$PAR{fromemail},$PAR{affiliate_collect},\@FIELDS);
		my $ran=create_unsubscribe_link($user);
		if($CONF{isdoi}){
			#double opt in
			if ($CONF{personalizeddoi}){			
				print $q->redirect($ENV{SCRIPT_NAME}."?act=pleaseconfirm&subscriber=$ran");
			}else{
				print $q->redirect($CONF{doiconfurl});
			}
		}else{
			#normal subscribe
			if ($CONF{personalizedsub}){			
				print $q->redirect($ENV{SCRIPT_NAME}."?act=thankyou&subscriber=$ran");
			}else{
				print $q->redirect($CONF{redirsub});
			}			
		}
		#print $q->redirect($CONF{redirsub});
		exit(1);
		
	}
}
&printheader;
my $add;
foreach (@FIELDS){
	$add.=<<ALL__;
		<TR class="data">
		<td align="right"><b>$_->{name}:</b></td>
		<TD>{fm_$_->{type}_dp$_->{key}}</TD></TR>
ALL__
}
$page->ChangeData('{additional_fields}',$add);
foreach(0..30){
	$page->add_element("days",$_)
}
$page->set_default_input("text","size",35);
$page->set_default_input("textarea","rows",4);
$page->set_default_input("textarea","columns",35);
$page->ParseData;
print $page->as_string;
#################
sub print_confirm_page{
	my $ran=$PAR{subscriber};
	print_error("$LNG{REG_CANTSHOW_CONFIRM}") unless $ran;
	my $user=FindUser($ran);
	print_error("$LNG{REG_SUBSCRIBER_WAS_NOT_FOUND}") unless $user;
	my %CONF=loadCONF($user->{fk_account});
	my $text;
	my $file="$TempatesDoiDir/$CONF{doiconftemplate}";
	if(-f $file){
		open(FILE,$file) || print_error("$LNG{REG_CAN_NOT_OPEN_FILE} $file $!");
		while(<FILE>){
			$text.=$_;		
		}
	}else{
		print_error("$LNG{REG_CAN_NOT_OPEN_FILE} $file");
	}
	$text=PersonalizeText($text,\%CONF,$user);
	printheader();
	print $text;
	exit;
}
sub print_thank_you_page{
	my $ran=$PAR{subscriber};
	print_error("$LNG{REG_CANTSHOW_THANKYOU}") unless $ran;
	my $user=FindUser($ran);
	print_error("$LNG{REG_SUBSCRIBER_WAS_NOT_FOUND}") unless $user;
	my %CONF=loadCONF($user->{fk_account});
	my $text;
	my $file="$TempatesSubscribeDir/$CONF{subscribetemplate}";
	if(-f $file){
		open(FILE,$file) || print_error("$LNG{REG_CAN_NOT_OPEN_FILE} $file $!");
		while(<FILE>){
			$text.=$_;		
		}
	}else{
		print_error("$LNG{REG_CAN_NOT_OPEN_FILE} $file");
	}
	$text=PersonalizeText($text,\%CONF,$user);
	printheader();
	print $text;
	exit;
}
sub FindUser{
	my $useruui=shift;
	my $user=select_one_db("SELECT * FROM ${PREF}user WHERE unsubscribe=?",$useruui);	
	return undef unless $user->{pk_user};
	$myuser=loaduser($user->{pk_user},undef,$user->{fk_account});
	return $myuser;
}
sub confirm{
	my @USERS;
	my %CONF=loadCONF($PAR{act});
	my $SQL="SELECT * FROM ${PREF}doi LEFT JOIN ${PREF}doiaccounts ON pk_doi=fk_doi WHERE ran=?";
	my $out=$db->prepare($SQL);
	$out->execute($PAR{id});
	&Error($SQL);
	my %output;
	my @TODO;
	my $doikey;
	while (%output=%{$out->fetchrow_hashref}){
		push(@USERS,$output{fk_user});
		$doikey=$output{pk_doi};	
	}
	if (@USERS){
		$db->do("UPDATE ${PREF}user SET  isact= 1, datereg=$NOW WHERE pk_user IN (".join(",",@USERS).")");
		if ($CONF{sendsubscr}){
			my $userid=select_one_db("SELECT pk_user,fk_account from ${PREF}user WHERE fk_account=? AND pk_user IN (".join(",",@USERS).")",$PAR{act});
			my $useraccount=$userid->{fk_account};
			$userid=$userid->{pk_user};
			if ($userid){
				my $subscrmess=select_one_db("SELECT pk_mess FROM ${PREF}mess WHERE fk_account=? AND typesend='subscribe'",$PAR{act});
				if ($subscrmess->{pk_mess}){
					$mess=load_mess($subscrmess->{pk_mess});
					$myuser=loaduser($userid,undef,$useraccount);
					$msg=GetMessForUser($myuser,\%CONF,$mess);
					my $leng=MIMEsendto($myuser->{email},$msg);
					MessageWasSent($userid,$subscrmess->{pk_mess});
				}
			}else{
				doLog("User id was not found - something wrong");
			}
		}
	}
	$db->do("DELETE FROM ${PREF}doiaccounts WHERE fk_doi=?",undef,$doikey);
	$db->do("DELETE FROM ${PREF}doi WHERE pk_doi=?",undef,$doikey);
	my $redirpage=$CONF{redirsub};
	if($CONF{personalizedsub}){
		print_error("$LNG{REG_ALREADY_CONFIRMED}")  unless(@USERS);
		my $user_pk=$USERS[0];
		my $user=loaduser($user_pk);
		my $ran=create_unsubscribe_link($user);
		$redirpage=$ENV{SCRIPT_NAME}."?act=thankyou&subscriber=$ran";
	}
	print_error("$LNG{REG_DOI_PAGE_IS_NOT_DEFINED}") unless($redirpage);
	print $q->redirect($redirpage);
	exit();	
}
sub unsubscribe{
	my $user=select_one_db("SELECT * FROM ${PREF}user WHERE unsubscribe=?",$PAR{unsubscribe} || $PAR{un});	
	my %CONF=();
	if ($user->{pk_user}){
		%CONF=loadCONF($user->{fk_account});
		my @unsubscribe_list=();
		if($CONF{unsub_unsubscribed_all}){
			map{push(@unsubscribe_list, $_) unless($_ eq $user->{fk_account})}keys %ACCOUNT;			
		}elsif(length($CONF{unsubscribe_when_unsubscribed})){
			my @uns_list=split /|/,$CONF{unsubscribe_when_unsubscribed};
			map{push(@unsubscribe_list, $_) unless($_ eq $user->{fk_account})}@uns_list;
		}
		foreach my $add_account_unsubscribe(@unsubscribe_list){
			my $user_add=select_one_db("SELECT * FROM ${PREF}user WHERE fk_account=? AND email=?",$add_account_unsubscribe,$user->{email});
			if($user_add->{pk_user}){
				doLog("$LNG{REG_LOG_DELETING_USER} $user_add->{name} $user_add->{email} $LNG{REG_FROM_ACCOUNT} $ACCOUNT{$add_account_unsubscribe}");
				DeleteUser($user_add->{pk_user});
			}
		}
		if($CONF{sendunsubscr}){
			my $messages=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='unsubscribe'",$user->{fk_account});
			if ($messages->{pk_mess}){
				$mess=load_mess($messages->{pk_mess});
				$myuser=loaduser($user->{pk_user},undef,$user->{fk_account});
				$msg=GetMessForUser($myuser,\%CONF,$mess,$user->{fk_account});
				my $leng=MIMEsendto($myuser->{email},$msg);
				MessageWasSent($user->{pk_user},$messages->{pk_mess});
			}
		}
		doLog("$LNG{REG_LOG_DELETING_USER} $user->{name} $user->{email} $LNG{REG_FROM_ACCOUNT} $ACCOUNT{$user->{fk_account}}");			
		DeleteUser($user->{pk_user});	
		IncreaseAccountCounter('unsubscribers',$user->{fk_account});
		my $userid=$user->{pk_user};
		if($CONF{isnotifunsubscr}){
			$msg = new MIME::Lite 
			From    =>"$user->{email}",
			To      =>"$CONF{adminname} <$CONF{adminemail}>",
			Subject =>"$LNG{REG_MSG_UNSUBSCRIBED_SUBJ}",
			Data    =>"$LNG{REG_MSG_UNSUBSCRIBED_BODY1} $user->{name} <$user->{email}> $LNG{REG_MSG_UNSUBSCRIBED_BODY2}: $ACCOUNT{$user->{fk_account}}";
			MIMEsendto($CONF{adminemail},$msg);
		}
		print $q->redirect($CONF{redirrem});
		exit();
	}else{
		%CONF=loadCONF();
		if(length($CONF{alreadyremoved})>7 and check_url($CONF{alreadyremoved})){
			print $q->redirect($CONF{alreadyremoved});
			exit;
		}
		printheader();
		print $q->start_html("SellWide.com Follow Up Mailing List Processor");
		print $q->h1("<center><span style=\"font-family: Tahoma, Verdana; font-size: 8pt\"><a href=\"http://www.sellwide.com/follow_up_mailing_list_processor.shtml\" target=\"_blank\">Powered by Follow Up Mailing List Processor</a></span><br><br><br><br><br><span style=\"font-family: Tahoma, Verdana; font-size: 20pt; font-weight: bold\">The email address is already unsubscribed</span></center>");
		print $q->end_html();
		exit();
	}
}
sub print_error{
	my $mess=shift;
	printheader();
	print $q->start_html($mess);
	print qq|<h1 align="center"><font color="red">$mess</font></h1>|;
	print $q->end_html();
	exit();
}
