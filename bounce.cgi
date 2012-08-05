#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Copyright 2006 SellWide Corporation                                #
# Last modified 08/29/2006                                           #
# Author: Konstantin Ursaloff                                        #
# Available at http://www.sellwide.com                               #
######################################################################
#                          COPYRIGHT NOTICE                          #
#                                                                    #
#     Copyright 2006 SellWide Corporation. All Rights Reserved.      #
#                                                                    #
# This script can be used as  long  as you don't change  this header #
# or  any  of  the  parts  that  give  me  credit  for writing this. #
#                                                                    #
# By using this script you agree to indemnify me from any  liability #
# that might arise from its use.                                     #
#                                                                    #
# Redistributing\selling  the  code  for  this program without prior #
# written consent is expressly forbidden.                            #
#                                                                    #
# Use for any  unauthorized  purpose is expressly prohibited by law, #
# and  may  result  in  severe  civil  and  criminal  penalties.     #
# Violators  will  be  prosecuted  to  the  maximum extent possible. #
#                                                                    #
#        YOU MAY NOT RESELL OR RELEASE THIS PROGRAM TO OTHERS        #
#                                                                    #
######################################################################
use lib('lib');
use Net::POP3;
require 'conf.cgi';
eval('require Mail::DeliveryStatus::BounceValidator');
if($@){
	printheader();
	print $q->start_html($LNG{BOUNCE_ERROR});
	print $q->h1($LNG{BOUNCE_ERROR_HEADER});
	print $q->p($LNG{BOUNCE_ERROR_DESCR1});
	print $q->p($LNG{BOUNCE_ERROR_DESCR2});
	print "<HR>\n";
	print "<P>$LNG{BOUNCE_ERROR_TXT}: $@ </P>\n";
	print $q->end_html();
	exit;
}
&par_prepare;&db_prepare;&sessiya;
die "Language keys was not loaded" unless keys %LNG;
$dparser::lang=\%LNG;
$shabl_page="$SHABL_DIR/bounce.html";
my $page=new hfparser(
		DATA=>$shabl_page
	);
$page->Hide('<!--HideBody-->');
my $body="";
if(not length($PAR{act})){
	$body=&get_accounts;
}elsif($PAR{act} eq 'totals'){
	$body=get_totals();
}elsif($PAR{act} eq 'accountpref'){
	$body=get_accountpref();
}elsif($PAR{act} eq 'test'){
	$body=get_accounttest();
}elsif($PAR{act} eq 'messages'){
	$body=get_messages();
}elsif($PAR{act} eq 'errorcode'){
	$body=get_errorcode();
}elsif($PAR{act} eq 'blacklist'){
	$body=get_blacklist();
}else{
	$body=qq|<h1 class="mess">$LNG{BOUNCE_ERROR_ACTION} $PAR{act} $LNG{BOUNCE_ERROR_ACTION_WAS_NOTFOUND}</h1>|;
}
$page->add_regesp('###DATA###',$body);
$page->ParseData;
&printheader;
$page->print;
exit;
#&print_all;
sub get_totals{
	my $page=new repparser (
		DATA=>$shabl_page,
		FROM=>'<!--TOTALS-->',TO=>'<!--TOTALS-->'
	);
	my $sql=qq|
SELECT count( `pk_bounce_message` ) as count, DATE_FORMAT( date, '\%d/\%m/\%Y' ) AS date_str, `hardsoft` , `action` 
FROM `${PREF}bounce_messages` 
GROUP BY DATE_FORMAT( date, '\%d/\%m/\%Y' ) , `hardsoft` , `action` 
ORDER BY `date` DESC |;
#return $sql;
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	my @rows=();
	my %dates=shift;
	while (my $output=$out->fetchrow_hashref){
		my $date_now=$output->{date_str};
		push(@rows,$date_now) unless(exists($dates{$date_now}));
		$dates{$date_now}{total}=$dates{$date_now}{total}+$output->{count};
		$dates{$date_now}{"$output->{hardsoft}_total"}=$dates{$date_now}{"$output->{hardsoft}_total"}+$output->{count};
		$dates{$date_now}{"$output->{hardsoft}_$output->{action}"}=$dates{$date_now}{"$output->{hardsoft}_$output->{action}"}+$output->{count};
		#$page->AddRow($output);
	}
	foreach my $date_now(@rows){
		my $info={};
		$info->{date}="<NOBR>".$date_now."</NOBR>";
		map{
			$info->{$_}=$dates{$date_now}{$_}
		}keys %{$dates{$date_now}};
		map{$info->{$_}="&nbsp;" unless exists($info->{$_})}qw(date total 1_total 2_total 1_0 1_1 1_2 1_3 2_0 2_1 2_2 2_3);
		#$info->{total}=$dates{$date_now}{total};
		$page->AddRow($info);		
	}
	$page->ParseData;
	return $page->as_string;	
}
sub get_accounttest{
	#print $q->header;
	my $page=new hfparser (
		DATA=>$shabl_page,
		FROM=>'<!--TEST-->',TO=>'<!--TEST-->'
	);
	my $account=select_one_db("SELECT * FROM ${PREF}bounce_account WHERE pk_bounce_account=?",$PAR{pk_bounce_account});
	
	my $testmess;
	my $count_bounce=0;
	$testmess="Connecting to $account->{pop3server} on port $account->{pop3port}\n";
	my $is_err;
	unless (defined ($pop = Net::POP3->new($account->{pop3server},Port=>$account->{pop3port}))){
		$testmess.="<font color=red>$LNG{BOUNCE_ERROR_CANT_OPEN_CONN} $account->{pop3server} : $!</font>";
		$is_err=1;	
	}
	if(defined ($pop)){
		my $max_mess_count=30;
		$testmess.="<font color=green>$LNG{BOUNCE_CONNECTED}</font>\n";
		$testmess.="$LNG{BOUNCE_CONNECTED_AUTH} $account->{pop3user} $LNG{BOUNCE_CONNECTED_AUTH_AND_PASS}\n";
		if(defined($pop->login($account->{pop3user}, $account->{pop3pass}))){
			$testmess.="<font color=green>$LNG{BOUNCE_CONNECTED_LOGGED}</font>\n";
			$testmess.="$LNG{BOUNCE_CONNECTED_FETCH}\n";
			if (defined ($messages = $pop->list)){
				$testmess.="<font color=green>$LNG{BOUNCE_CONNECTED_YOU_HAVE} ".scalar(keys %$messages)." $LNG{BOUNCE_CONNECTED_YOU_HAVE_MESS}</font>\n";
				$testmess.="$LNG{BOUNCE_CONNECTED_LOADING} $max_mess_count $LNG{BOUNCE_CONNECTED_LOADING_MESS}\n";				
			}else{
				$testmess.="<font color=green>$LNG{BOUNCE_CONNECTED_LOADING_EMPTY}</font>\n";				
			}
			my $no;
			foreach $msgid (sort {$b<=>$a} keys %$messages){
				$no++;
				last if $no>$max_mess_count;
				my $message = $pop->get($msgid);
				$pop->reset();
				if (defined $message){
					#$testmess.="Parsing: ";
					#my $bounce = eval { Mail::DeliveryStatus::BounceValidator->new($message, {'log'=> sub{print "".shift."\n"}}) };
					my $bounce = eval { Mail::DeliveryStatus::BounceValidator->new($message, {'log'=> sub{}}) };
					if ($@){
						$testmess.="<font color=red>$LNG{BOUNCE_ERROR_VALIDATOR}:$@</font>\n";
					}else{
						if($bounce->is_bounce()){
							$count_bounce++;
							$testmess.="...$LNG{BOUNCE_LOAD_MSG} $msgid \n";
							$testmess.="<font color=green>OK</font>\n";							
							$testmess.="$LNG{BOUNCE_LOAD_MSG_IS_BOUNC}\n";
							$testmess.="$LNG{BOUNCE_LOAD_MSG_EMAIL_IS}: ".$bounce->email."\n";
							$testmess.="$LNG{BOUNCE_LOAD_MSG_EMAIL_IS_DIAG}:\n----------------------------\n" ;
							$testmess.=$bounce->diagnostic_as_string;
							$testmess.="----------------------------\n";
							$testmess.="\n<HR>\n";
						}else{
							#$testmess.="Not bounced message\n";						
						}
					}

				}else{
					$testmess.="<font color=red>$LNG{BOUNCE_LOAD_MSG_CANT_LOAD}</font>\n";					
				}
				#last if($no>25);
			}
			$count_bounce="\n$LNG{BOUNCE_COUNT_TOTAL} <B>$count_bounce</b> $LNG{BOUNCE_COUNT_TOTAL_MSGS}\n";
			$testmess.="<font color=green><B>$LNG{BOUNCE_TEST_OK}</B></font>\n";				
			$pop->quit();			
		}else{
			$testmess.="<font color=red>$LNG{BOUNCE_TEST_ERROR}: $!</font>\n";
			$is_err=1;
			$pop->quit();
		}
	}
	$testmess.=qq|<font color=red>Errors detected please <a href="$ENV{SCRIPT_NAME}?ses=$PAR{ses}&act=accountpref&pk_bounce_account=$PAR{pk_bounce_account}"> check your settings</P></font>| if $is_err;
	$page->add_regesp('{TEST}',qq|<PRE>\n$testmess\n</PRE><P><a href="$ENV{SCRIPT_NAME}?ses=$PAR{ses}">Back to accounts</a>|);
	$page->ParseData;
	return $page->as_string;
}
sub get_accountpref{
	my $page=new hfparser (
		DATA=>$shabl_page,
		FROM=>'<!--EDIT-->',TO=>'<!--EDIT-->'
	);
	my $isnew=0;
	unless($PAR{pk_bounce_account}){
		$isnew=1;
	}
	if($PAR{issubmit}){
		my @all_fields=qw(pop3server pop3port pop3user pop3pass hardcount softcount deleteemails bounceaction isaddtoban);
		my @required_fields=qw(pop3server pop3port pop3user pop3pass hardcount softcount bounceaction);
		map{$page->set_error($_,'requered') unless length($PAR{$_})}@required_fields;
		map{$page->set_error($_,'number requered') if($PAR{$_}=~/[^0-9]/)}qw(pop3port hardcount softcount);
		unless($page->is_error()){
			my $data={};
			map{$data->{$_}=$PAR{$_}}@all_fields;
			if($isnew){
				insert_db("${PREF}bounce_account",$data);
			}else{
				update_db("${PREF}bounce_account",$data,{pk_bounce_account=>$PAR{pk_bounce_account}});
			}
			print $q->redirect("$ENV{SCRIPT_NAME}?ses=$PAR{ses}");
			exit;
		}
	}
	$page->set_def('pop3port',110);	$page->set_input('pop3port',{size=>4});
	$page->set_def('hardcount',1);	$page->set_input('hardcount',{size=>2});
	$page->set_def('softcount',3);	$page->set_input('softcount',{size=>2});
	$page->add_element('bounceaction',1,"$LNG{BOUNCE_PAGE_REM_MAIL_ALL_ACC}");
	$page->add_element('bounceaction',2,"$LNG{BOUNCE_PAGE_SET_STATUS_INACT}");

	unless($isnew){
		my $account=select_one_db("SELECT * FROM ${PREF}bounce_account WHERE pk_bounce_account=?",$PAR{pk_bounce_account});
		map{$page->set_def($_,$account->{$_})}%$account;
	}
	
	$page->add_regesp('{header}',"$LNG{BOUNCE_PAGE_ADD_NEW_POP}")if($isnew);
	$page->add_regesp('{header}',"$LNG{BOUNCE_PAGE_EDIT_POP}")unless($isnew);
	$page->ParseData;
	return $page->as_string;
}
sub delete_bounce_account{
	my $id=shift;	
	$db->do("DELETE FROM ${PREF}bounce_account WHERE pk_bounce_account=?",undef,$id);
	&Error;
}
sub get_accounts{
	my $page=new repparser (
		DATA=>$shabl_page,
		FROM=>'<!--ACCOUNTS-->',TO=>'<!--ACCOUNTS-->'
	);
	if($PAR{'delete'} || $PAR{activate}||$PAR{deactivate}){
		map{
			if($PAR{'delete'}){
				delete_bounce_account($_);	
			}elsif($PAR{activate}){
				update_db("${PREF}bounce_account",{isact=>1},{pk_bounce_account=>$_});			
			}elsif($PAR{deactivate}){
				update_db("${PREF}bounce_account",{isact=>0},{pk_bounce_account=>$_});
			}
		}$q->param('id');
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}");
		exit;	
	}
		my $sql="SELECT * FROM ${PREF}bounce_account";
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	while (my $output=$out->fetchrow_hashref){
		$output->{status}=qq|<font color="red">Disabled</font>| unless $output->{isact};
		$output->{status}=qq|<font color="green"><B>OK</B></font>| if $output->{isact};
		$page->AddRow($output);
	}
	$page->ParseData;
	return $page->as_string;
}
sub get_messages{
	if($PAR{deleteallmessages}){
		$db->do("DELETE FROM ${PREF}bounce_messages");
		print $q->redirect("$ENV{SCRIPT_NAME}?ses=$PAR{ses}&act=$PAR{act}");
		exit;		
	}
	if($PAR{inactivateprospect} || $PAR{activateprospect} || $PAR{deletemessages} ||$PAR{removeprospect}){
		my @ban_mess=$q->param('id');
		if(@ban_mess){
			my $IN_ID=join(',',@ban_mess);
			my $sql="SELECT * FROM `${PREF}bounce_messages` WHERE pk_bounce_message IN ($IN_ID)";
			my $out=$db->prepare($sql);
			$out->execute();
			&Error($sql);
			while (my $output=$out->fetchrow_hashref){
				if($PAR{deletemessages}){
					$db->do("DELETE FROM ${PREF}bounce_messages WHERE pk_bounce_message=?",undef,$output->{pk_bounce_message});
					&Error("DELETE FROM ${PREF}bounce_messages");
				}elsif($PAR{removeprospect}){
					my $sql="SELECT pk_user FROM `${PREF}user` WHERE email=?";
					my $out1=$db->prepare($sql);
					$out1->execute($output->{email});
					while (my $prospect=$out1->fetchrow_hashref){					
						DeleteUser($prospect->{pk_user});
					}
				}elsif($PAR{inactivateprospect}){
					update_db("${PREF}user",{isact=>0},{email=>$output->{email}});
				}elsif($PAR{activateprospect}){
					update_db("${PREF}user",{isact=>1},{email=>$output->{email}});
				}
				unless($PAR{deletemessages}){
					update_db("${PREF}bounce_messages",{action=>4},{pk_bounce_message=>$output->{pk_bounce_message}});
				}
			}
		}
		print $q->redirect("$ENV{SCRIPT_NAME}?ses=$PAR{ses}&act=$PAR{act}");
		exit;
	}
	my %act_count;
	my %inact_count;
	foreach my $isact_now (0,1){
		my $sql = qq|
		SELECT COUNT(DISTINCT pk_user) as count , ${PREF}bounce_messages.email as email
		FROM ${PREF}bounce_messages
		LEFT  JOIN ${PREF}user ON ${PREF}user.email = ${PREF}bounce_messages.email
		WHERE isact = $isact_now
		GROUP  BY ${PREF}bounce_messages.email
		|;
		my $out=$db->prepare($sql);
		$out->execute();
		&Error($sql);
		while (my $output=$out->fetchrow_hashref){
			if($isact_now){
				$act_count{$output->{email}}=$output->{count};
			}else{
				$inact_count{$output->{email}}=$output->{count};
			}
		}
	}
	my $page=new repparser (
		DATA=>$shabl_page,
		FROM=>'<!--MESSAGESREPORT-->',TO=>'<!--MESSAGESREPORT-->'
	);
	$page->set_input('status',{size=>5});
	my %stat=(
			""=>"-----",
			0=>"$LNG{BOUNCE_STATUS_WAITING}",
			1=>"$LNG{BOUNCE_STATUS_REMOVED}",
			2=>"$LNG{BOUNCE_STATUS_INACTIV}",
			3=>"$LNG{BOUNCE_STATUS_NOTFOUND}",
			4=>"$LNG{BOUNCE_STATUS_PROC_MAN}"	
		);
	my $sql="Select * from ${PREF}bounce_account";
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	$page->add_element('fk_bounce_account',"","-----");
	while (my $output=$out->fetchrow_hashref){
		$page->add_element('fk_bounce_account',$output->{pk_bounce_account},"$output->{pop3user} - $output->{pop3server}");	
	}
	map{$page->add_element('action',$_,$stat{$_})}keys %stat;
	$page->add_element('hardsoft',"","-----");
	$page->add_element('hardsoft',1,"$LNG{BOUNCE_SORT_HARD}");
	$page->add_element('hardsoft',2,"$LNG{BOUNCE_SORT_SOFT}");
	$page->add_element('orderby','date',"$LNG{BOUNCE_SORT_DATE}");
	$page->add_element('orderby','email',"$LNG{BOUNCE_SORT_MAIL}");
	$page->add_element('ordertype','ASC',"$LNG{BOUNCE_SORT_ASC}");
	$page->add_element('ordertype','DESC',"$LNG{BOUNCE_SORT_DESC}");
	$page->set_def('ordertype','DESC');
	$page->set_def('orderby','date');
	$PAR{orderby}='date' unless(length($PAR{orderby}));
	$PAR{ordertype}='DESC' unless(length($PAR{ordertype}));
	my @rule=();
	map{push(@rule,"$_=$PAR{$_}")}keys %PAR;
	push(@rule,"act2=export");
	$page->add_regesp('{exportrule}',join('&',@rule));
	my @where=();
	push(@where, "email LIKE ".$db->quote('%'.$PAR{email}.'%')) if(length($PAR{email}));
	push(@where, "reason LIKE ".$db->quote('%'.$PAR{reason}.'%')) if(length($PAR{reason}));
	map {push(@where, "$_ = ".$PAR{$_}) if(length($PAR{$_}))} qw(fk_bounce_account hardsoft action);
	my $WHERE="WHERE ".join(" AND ",@where) if @where;
#SELECT count( `pk_bounce_message` ) , DATE_FORMAT( date, '%d/%m/%Y' ) AS date_str, `hardsoft` , `action` 
#FROM `swd_bounce_messages` 
#GROUP BY DATE_FORMAT( date, '%d/%m/%Y' ) , `hardsoft` , `action` 
#ORDER BY `date` DESC
#
	
	my $sql=qq|
SELECT * , DATE_FORMAT( date, '%d/%m/%Y' ) AS date_str,
IF(action=0,'Waiting',
	IF(action=1,'Prospect&nbsp;removed',
		IF(action=2,'Prospect&nbsp;inactivated',
			IF(action=3,'Prospect&nbsp;not&nbsp;found',
			'Processed&nbsp;manually'	
			)	
		)	
	)
) AS action_str,
IF(hardsoft=1,'Hard','Soft')AS hardsoft_str
FROM `${PREF}bounce_messages`
$WHERE
ORDER BY $PAR{orderby} $PAR{ordertype}
	|;


	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	my %export;
	while (my $output=$out->fetchrow_hashref){
		if($PAR{withprospects}){
			next unless($inact_count{$output->{email}} || $act_count{$output->{email}});
		}
		$export{$output->{email}}++;
		$output->{inact}=$inact_count{$output->{email}};
		$output->{act}=$act_count{$output->{email}};
		
		$output->{reason}=~s#(https?://[^\s]+)#<a href="$1" target="_blank">$1</a>#gis;
#		$output->{status}=qq|<font color="red">Disabled</font>| unless $output->{isact};
#		$output->{status}=qq|<font color="green"><B>OK</B></font>| if $output->{isact};
		$page->AddRow($output);
	}
	if($PAR{act2} eq 'export'){
		print $q->header('text/plain');
		print "########################################\n";
		print "#Extracted emails from bounced messages#\n";
		print "#By SellWide Mailing List Processor    #\n";
		print "#Current date: ".localtime()."#\n";
		print "########################################\n\n";	
		print join("\n",sort{$a cmp $b} keys %export);
		exit;
	}
	$page->ParseData;
	return $page->as_string;
}
sub get_errorcode{
	my $page=new dparser (
		DATA=>$shabl_page,
		FROM=>'<!--ERRORCODE-->',TO=>'<!--ERRORCODE-->'
	);
	my $descr;
	eval{
	  use Mail::DeliveryStatus::BounceStatus; 
	  my $explainer=Mail::DeliveryStatus::BounceStatus->new($PAR{code});
	   $descr=$explainer->as_string;
	};
	$page->add_regesp('{code}',$PAR{code});
	$page->add_regesp('{DESCRIPTION}',$descr);
	$page->ParseData;
	return $page->as_string;	
}

sub get_blacklist{
	if($PAR{'delete'}){
		
		my @emails=$q->param('id');
		if(@emails){
			@emails=map{"email=".$db->quote($_)}@emails;
			my $sql="DELETE FROM ${PREF}bounce_banemails WHERE ".join(" OR ",@emails);
			$db->do($sql);
			&Error($sql);
		}
	}
	my $page=new repparser (
		DATA=>$shabl_page,
		FROM=>'<!--BLACKLIST-->',TO=>'<!--BLACKLIST-->'
	);
	$page->add_regesp('{mess}','');
	if($PAR{process} eq 'remove' and length($PAR{bulklist})){
		my @list = split(/\r?\n/,$PAR{bulklist});
		my @remove_list=();
		map{push(@remove_list,$_) if length($_)}@list;
		@remove_list=map{"email LIKE ".$db->quote('%'.$_.'%')}@remove_list;
		if(@remove_list){
			my $sql="SELECT * FROM ${PREF}bounce_banemails WHERE ".join(" OR ",@remove_list);
			my $count=GetSQLCount($sql);
			unless($PAR{confirm}){
				my $mess= "<h1 class=\"mess\">$count emails will be removed from BlackList</h1>";
				if($count){
					my $textarea=$q->hidden(-name=>'bulklist').$q->hidden(-name=>'ses').$q->hidden(-name=>'act').$q->hidden(-name=>'process');
					$mess.=<<ALL__;
					<FORM action="$ENV{SCRIPT_NAME}" method="POST">
$textarea
<input type="submit" name="confirm" value="$LNG{BOUNCE_INPUT_REM_PROSP}" class="BUTTONmySmall" onClick="return confirm('$LNG{BOUNCE_INPUT_REM_PROSP_SURE} $count $LNG{BOUNCE_INPUT_REM_PROSP_SURE_MAILS}?');">
&nbsp;&nbsp;&nbsp;&nbsp;
<INPUT type="submit" name="return" value="$LNG{BOUNCE_INPUT_REM_PROSP_CANCEL}" onClick="history.back()" class="BUTTONmySmall">
</FORM>
ALL__
				}else{
					$mess.=qq|<INPUT type="submit" value="$LNG{BOUNCE_INPUT_BACK_BLACKLIST}" name="return" onClick="history.back()" class="BUTTONmySmall">|;
				}
				return $mess;
			}else{
				$db->do("DELETE FROM ${PREF}bounce_banemails WHERE ".join(" OR ",@remove_list));
				$page->add_regesp('{mess}',"<h1 class=\"mess\">$count $LNG{BOUNCE_EMAILS_WERE_REM}</h1>");
			}
		}
	}
	if($PAR{process} eq 'import' and length($PAR{importlist})){
		my @list = split(/\r?\n/,$PAR{importlist});
		my $countadd=0;
		foreach my $email(@list){
			next unless(checkemail($email));
			next if(GetSQLCount("SELECT * FROM ${PREF}bounce_banemails WHERE email=?",$email));
			$countadd++;
			insert_db("${PREF}bounce_banemails",{email=>$email});

		}
		$page->add_regesp('{mess}',"<h1 class=\"mess\">$countadd $LNG{BOUNCE_EMAILS_WERE_ADD}</h1>");		
	}
	$page->add_regesp('{email}',$PAR{email});
	$page->set_input('blacklist_error',{size=>40});
	$CONF{blacklist_error}="$LNG{BOUNCE_ERROR_DELIVER_MSGS}" unless(length($CONF{blacklist_error}));
	map{$page->set_def($_,$CONF{$_})}qw(blacklist_error useblacklist);
	
	if($PAR{save}){
		if($PAR{useblacklist}){
			$page->set_error('blacklist_error','required') unless (length($PAR{blacklist_error}));
		}
		unless($page->is_error){
			save_config(0,'blacklist_error',$PAR{blacklist_error});
			save_config(0,'useblacklist',$PAR{useblacklist});		
			$page->add_regesp('{mess}',"<h1 class=\"mess\">$LNG{BOUNCE_SETTS_UPDATED}</h1>");
		}
	}	
	my $where;
	if (length($PAR{email})){
		$where="WHERE email LIKE ".$db->quote('%'.$PAR{email}.'%');	
	}
	my $sql="SELECT * FROM ${PREF}bounce_banemails $where";
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	my %export;
	while (my $output=$out->fetchrow_hashref){
		$export{$output->{email}}++;
		$page->AddRow($output);
	}
	if($PAR{act2} eq 'export'){
		print $q->header('text/plain');
		print "########################################\n";
		print "#Exported blacklist emails             #\n";
		print "#By SellWide Mailing List Processor    #\n";
		print "#Current date: ".localtime()."#\n";
		print "########################################\n\n";	
		print join("\n",sort{$a cmp $b} keys %export);
		exit;
	}
	$page->ParseData();
	return $page->as_string;
}


