#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 03/21/2007                                           #
######################################################################
use lib('lib');
require 'conf.cgi';
###
%CONF=(); %PAR=();%ACCOUNT=();
###
&par_prepare;
&db_prepare;
unless(keys %LNG){
	&printheader;
	print $q->start_html("Error");
	print $q->h1("Language keys was not loaded");
	print $q->p("Can not find file <B>shabl/$CONF{langnow}.txt");
	print $q->end_html;
	exit;
}
$dparser::lang=\%LNG;
#map{$LNG{$_}="|$LNG{$_}|"}keys %LNG;
local %ACT=        (
        ""        =>\&print_frameset,
        account   =>\&print_account,
	signatures=>\&print_manage_signatures,
	manageaccount=>\&print_manage_account,
	openhtmleditor=>\&openXinha,
	lngset    =>\&print_set_leng,
        mainbody  =>\&print_main,
	'stat'=> =>\&print_stat,
	settings  =>\&print_settings,
	getfile  =>\&print_getfile,
	delfile  =>\&print_delfile,
	doimess	 =>\&print_doimess,
	subscrmess=>\&print_subsmess,
	unsubscrmess=>\&print_unsubsmess,
	showmess=>\&print_show_mess,
	showrfcmess=>\&print_show_rfc_mess,
	changehtmleditor=>\&print_change_editor,
	testsend=>\&print_test_send,
	statdaily=>\&print_statdaily,
	logout=>\&print_logout
	
);
local @ACCOUNTMENU=(
        {name=>$LNG{ACCOUNTMENU_MAIN},    params=>{act2=>""}},
        {name=>$LNG{ACCOUNTMENU_OPTIONS},params=>{act2=>"config"},
		description=>$LNG{ACCOUNTMENU_OPTIONS_DESCR},
		nextlevel=>[
			{
				name=>$LNG{ACCOUNTMENU_OPTIONS},
				params=>{act3=>""},
				description=>''				
			},
			{
				name=>$LNG{ACCOUNTMENU_HTML_RSS},
				params=>{act3=>"rss"},
				description=>''			
			}
		]
	},
        {name=>$LNG{ACCOUNTMENU_HTML_FORM},    params=>{act2=>"columns"},
		description=>$LNG{ACCOUNTMENU_HTML_FORM_DESCR},
		nextlevel=>[
			{
				name=>$LNG{ACCOUNTMENU_HTML_FORM},
				params=>{act3=>""},
				description=>''				
			},
			{
				name=>$LNG{HTML_FORM_FIELDS},
				params=>{act3=>"fields"},
				description=>''			
			},
			{
				name=>$LNG{HTML_FORM_OPTIONS},
				params=>{act3=>"settings"},
				description=>''			
			},
			{
				name=>$LNG{HTML_FORM_INTEGRATION},
				params=>{act3=>"integration"},
				description=>''			
			}			

		]	
	},
	
#        {name=>$LNG{ACCOUNTMENU_HTML_RSS},    params=>{act2=>"rss"},
#		description=>$LNG{ACCOUNTMENU_HTML_RSS_DESCR}},
	{name=>$LNG{ACCOUNTMENU_SUBSCR_MAN}, params=>{act2=>"users_new"},
		description=>$LNG{ACCOUNTMENU_SUBSCR_MAN_DESCR},
		nextlevel=>[
			{
				name=>$LNG{ACCOUNTMENU_SUBSCR_MAN},
				params=>{act3=>""},
				description=>''				
			},
			{
				name=>(($PAR{reckey} and ($PAR{act3}eq"userform"))?"$LNG{ACCOUNT_MENU_EDIT_CURRENT_PROSPECT}":$LNG{PROSPMENU_ADD_PROSP}),
				params=>{act3=>"userform"},
				description=>''				
			},
			{
				name=>$LNG{PROSPMENU_IMPORT},
				params=>{act3=>"import"},
				description=>'',
				nextlevel=>[
					{
						name=>$LNG{IMPORT_FROM_TEXT},
						params=>{act4=>""},
						description=>''
					},
					{
						name=>$LNG{IMPORT_FROM_TAB_DELMITTED},
						params=>{act4=>"tab"},
						description=>''
					}					
						
				]
			},
			{
				name=>$LNG{PROSPMENU_EXPORT},
				params=>{act3=>"export"},
				description=>'',
				nextlevel=>[
					{
						name=>$LNG{PROSPMENU_EXPORT},
						params=>{act4=>""},
						description=>''
					},
					{
						name=>$LNG{EXPORT_TO_TAB_DELMITTED},
						params=>{act4=>"tab"},
						description=>''
					}					
						
				]
			},			
			{
				name=>$LNG{PROSPMENU_COPY},
				params=>{act3=>'copy'},
				description=>'',
			},			
			{
				name=>$LNG{PROSPMENU_BULK_REMOVE},
				params=>{act3=>'bulk'},
				description=>'',
			}			
			]	
	
	},
        {name=>$LNG{ACCOUNTMENU_EDIT_MESS}, params=>{act2=>"mess"},
		description=>$LNG{ACCOUNTMENU_EDIT_MESS_DESCR}},
        {name=>$LNG{ACCOUNTMENU_LINKS}, params=>{act2=>"links"},
		description=>$LNG{ACCOUNTMENU_LINKS_DESCR},
		nextlevel=>[
			{
				name=>$LNG{ACCOUNTMENU_LINKS},
				params=>{modelog=>""},
				description=>'',
				add_params=>[qw(datefilter)]
			},
			{
				name=>$LNG{ACCOUNTMENU_LINKS_MESS_STAT},
				params=>{modelog=>"mess"},
				description=>'',
				add_params=>[qw(datefilter)]
			},

			{
				name=>$LNG{ACCOUNTMENU_LINKS_ACT_PROSP},
				params=>{modelog=>"prospects"},
				description=>'',
				add_params=>[qw(datefilter)],
			},			
			{
				name=>$LNG{ACCOUNTMENU_LINKS_CLICKS},
				params=>{modelog=>"clicks"},
				description=>'',
				add_params=>[qw(datefilter)],
			},			
			]
	}
	
);
local @SETTINGSMENU=(
        {name=>$LNG{SETTINGSMENU_MAIN},    params=>{act2=>""}},
        {name=>$LNG{SETTINGSMENU_PERSONAL},params=>{act2=>"personal"},
		description=>$LNG{SETTINGSMENU_PERSONAL_DESCR}},
        {name=>$LNG{SETTINGSMENU_SENDING_OPTIONS},    params=>{act2=>"smtp"},
		description=>$LNG{SETTINGSMENU_SENDING_OPTIONS_DESCR}},
        {name=>$LNG{SETTINGSMENU_ACCESS},    params=>{act2=>"pass"},
		description=>$LNG{SETTINGSMENU_ACCESS_DESCR}},
	{name=>$LNG{SETTINGSMENU_TIME_SYNC},    params=>{act2=>"timecorr"},
		description=>$LNG{SETTINGSMENU_TIME_SYNC_DESCR}},
	{name=>$LNG{SETTINGSMENU_PERFOM},    params=>{act2=>"test"},
		description=>$LNG{SETTINGSMENU_PERFOM_DESCR}},
	{name=>$LNG{SETTINGSMENU_BACUP_RESTORE},    params=>{act2=>"backup"},
		description=>$LNG{SETTINGSMENU_BACUP_RESTORE_DESCR}}
);
local @STATMENU=(
        {name=>$LNG{STATMENU_MAIN},    params=>{act2=>""}},
  	{name=>$LNG{STATMENU_ACT_LOGS},    params=>{act2=>"log"},
		description=>$LNG{STATMENU_ACT_LOGS_DESCR}},
  	{name=>$LNG{STATMENU_CURRENT_BROADCAST},    params=>{act2=>"curlog"},
		description=>$LNG{STATMENU_CURRENT_BROADCAST_DESCR}},
  	{name=>$LNG{STATMENU_TOTALS},    params=>{act2=>"total"},
		description=>$LNG{STATMENU_TOTALS_DESCR},
		nextlevel=>[
			{
				name=>$LNG{STATMENU_TOTALS_SENT_MESS},
				params=>{modelog=>""},
				description=>'',
				add_params=>[qw(day1 day2 month1 month2 year1 year2)]
			},
			{
				name=>$LNG{STATMENU_TOTALS_SUBSCRIBERS},
				params=>{modelog=>"subscribers"},
				description=>'',
				add_params=>[qw(day1 day2 month1 month2 year1 year2)]
			},
			{
				name=>$LNG{STATMENU_TOTALS_PROSPECTS},
				params=>{modelog=>"account"},
				description=>'',
				add_params=>[qw(day1 day2 month1 month2 year1 year2)],
			},			
			]
	},	
);

my $address=$ENV{HTTP_HOST};
my $scriptdir=$ENV{SCRIPT_NAME};
(my $src=$scriptdir)=~s#[^/]*$##;
save_config(0,"serverurl","http://$address${src}");
&sessiya;
&process_all;

sub ReorderAccounts{
	my $count;
	my $sql="SELECT * from ${PREF}account ORDER by position asc , name asc";
	my $out=$db->prepare($sql);
	$out->execute();	
	my $count=0;
	while (my $output=$out->fetchrow_hashref){
		$count++;
		update_db("${PREF}account", {position=>$count},{pk_account=>$output->{pk_account}}) if($output->{position}!=$count);
	}
	return $count;
}
sub print_accountreport{
	my $account_count=ReorderAccounts();
	if($PAR{modify} eq 'chstatus'){
		#die $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&reload=1");
		$db->do("UPDATE ${PREF}account SET isact = IF(isact=1,0,1) WHERE pk_account=? LIMIT 1",undef,$PAR{id});
		&Error;
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&reload=1");
		exit;		
	}
	if($PAR{modify} eq 'delete'){
		DeleteAccount($PAR{id});
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&reload=1");
		exit;		
	}
	if($PAR{modify} eq 'moveup'){
		my $hr=select_one_db("SELECT * FROM ${PREF}account WHERE pk_account=?",$PAR{id});
		#die $hr->{position};
		update_db("${PREF}account",{position=>$hr->{position}},{position=>$hr->{position}-1});
		update_db("${PREF}account",{position=>$hr->{position}-1},{pk_account=>$PAR{id}});
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&reload=1");
		exit;		
	}
	if($PAR{modify} eq 'movedown'){
		my $hr=select_one_db("SELECT * FROM ${PREF}account WHERE pk_account=?",$PAR{id});
		update_db("${PREF}account",{position=>$hr->{position}},{position=>$hr->{position}+1});
		update_db("${PREF}account",{position=>$hr->{position}+1},{pk_account=>$PAR{id}});
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&reload=1");
		exit;		
	}	
	my $page=new repparser
	DATA=>"$SHABL_DIR/manage_accounts.html",TO => "#end_report",FROM=>"#start_report";
	map{$page->add_regesp("{".$_."}",$PAR{$_})}keys %PAR;
	$page->Hide('<!--IFRELOAD-->') unless ($PAR{reload});
	my $sql="SELECT * from ${PREF}account ORDER by position asc , name asc";
	my $out=$db->prepare($sql);
	$out->execute();
	while (my $output=$out->fetchrow_hashref){
		$output->{img} = "content.cgi?get=image&mode=gif&f=";
		$output->{img}.=$output->{isact}?'active':'inact';
		$output->{confirm_activation}=$output->{isact}?$LNG{CONFIRM_DISABLING_ACCOUNT}:$LNG{CONFIRM_ENABLING_ACCOUNT};
		$output->{status}=$output->{isact}?$LNG{MESS_ACTIVE}:$LNG{MESS_INACTIVE};
		$output->{statustitle}=$output->{isact}?$LNG{ACCOUNT_STATUS_ACTIV_DESCR}:$LNG{ACCOUNT_STATUS_INACTIV_DESCR};
		if($output->{position}==1){
			$output->{moveup}=qq|<img src="img/sp.gif" width="16" height="16" border="0">|;
		}else{
			$output->{moveup}=qq|<a href="$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&modify=moveup&id=$output->{pk_account}"><img src="content.cgi?get=image&mode=gif&f=move_task_up" width="16" height="16" border="0"></a>|;
		}
		if($output->{position}==$account_count){
			$output->{movedown}=qq|<img src="img/sp.gif" width="16" height="16" border="0">|;
		}else{
			$output->{movedown}=qq|<a href="$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&modify=movedown&id=$output->{pk_account}"><img src="content.cgi?get=image&mode=gif&f=move_task_down" width="16" height="16" border="0"></a>|;
		}
		$page->AddRow($output);
	}
	$page->ParseData;
	return $page->as_string;

}
sub print_account_pref{
	my $page=new hfparser
	DATA=>"$SHABL_DIR/manage_accounts.html",TO => "#end_account_pref",FROM=>"#start_account_pref";
	if($PAR{issubmit}){
		$PAR{name}=~s/^\s+//;
		$PAR{name}=~s/\s+$//;
		$page->set_error('name',"$LNG{ERROR_REQUIRED}") unless length($PAR{name});
		if($PAR{id}){
			$page->set_error('name',ucfirst("$LNG{ERROR_IS_ALREADY_EXISTS}")) if GetSQLCount("SELECT * FROM ${PREF}account WHERE name=? AND pk_account<>?",$PAR{name},$PAR{id});
		}else{
			$page->set_error('name',ucfirst("$LNG{ERROR_IS_ALREADY_EXISTS}")) if GetSQLCount("SELECT * FROM ${PREF}account WHERE name=?",$PAR{name});
		}
		unless($page->is_error){
			if($PAR{id}){
				update_db("${PREF}account",{name=>sequre($PAR{name}),descr=>sequre($PAR{descr})},{pk_account=>$PAR{id}});
			}else{
				my $count=insert_db("${PREF}account",{name=>sequre($PAR{name}),isact=>1,descr=>sequre($PAR{descr})});
				if ($PAR{clone}){
					DublicateAccountTable("${PREF}conf",$PAR{clone},$count,undef,"fk_account");
					DublicateAccountTable("${PREF}fields",$PAR{clone},$count,"pk_fields","fk_account");
					DublicateAccountTable("${PREF}mess",$PAR{clone},$count,"pk_mess","fk_account");
					$db->do("UPDATE ${PREF}mess SET sent=0 WHERE fk_account=?",undef,$count);
				}
			}
			print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&reload=1");
			exit;		
		}


	}
	unless($PAR{id}){
		unless($PAR{clone}){
			$page->add_regesp('{ACTION_VALUE}',$LNG{ACCOUNT_NEW});
		}else{
			my $hr=select_one_db("SELECT * FROM ${PREF}account WHERE pk_account=?",$PAR{clone});
			$page->add_regesp('{ACTION_VALUE}',"$LNG{ACCOUNT_CLONE} $hr->{name}");
		}

	}else{
		$page->add_regesp('{ACTION_VALUE}',$LNG{ACCOUNT_EDIT});

	}
	if($PAR{id}){
		my $hr=select_one_db("SELECT * FROM ${PREF}account WHERE pk_account=?",$PAR{id});
		map{$page->set_def($_,$hr->{$_})}keys %$hr;
	}
	$page->ParseData;
	return $page->as_string;
}
sub print_manage_account{
	my %map;
	%map=(	""       =>\&print_accountreport,
		accountpref  =>\&print_account_pref
	);
	$main_page=new dparser(
		DATA=>"$SHABL_DIR/main-settings.html"
	);
	#$main_page->add_regesp('{main_menu}',get_account_menu(\@SETTINGSMENU));
	$main_page->add_regesp('{main_menu}',"");
	my $func_ref;
	if ($map{$PAR{act2}}) {
		$func_ref=$map{$PAR{act2}};
	}else{
		$func_ref=sub{return $q->h1($LNG{INCORRECT_URL})}
	}
	$main_page->add_regesp('###TITLE###',$LNG{MANAGE_ACCOUNTS});
	$main_page->add_regesp('{body}',&$func_ref);
	$main_page->ParseData;
	&printheader;
	$main_page->print;		
}
sub print_signatures_report{
	if($PAR{modify} eq 'delete'){
		$db->do("DELETE FROM ${PREF}signatures WHERE pk_signature=?",undef,$PAR{id});
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}");
		exit;		
	}
	my $page=new repparser
	DATA=>"$SHABL_DIR/manage_signatures.html",TO => "#end_report",FROM=>"#start_report";
	map{$page->add_regesp("{".$_."}",$PAR{$_})}keys %PAR;
	my $sql="SELECT * from ${PREF}signatures ORDER by name asc";
	my $out=$db->prepare($sql);
	$out->execute();
	while (my $output=$out->fetchrow_hashref){
		my $sql2="SELECT * FROM ${PREF}mess WHERE mess LIKE ".$db->quote('%[SIGNATURE_'.$output->{name}.']%')." OR messhtml LIKE ".$db->quote('%[SIGNATURE_'.$output->{name}.']%')." ORDER by fk_account";
		my $out2=$db->prepare($sql2);
		$out2->execute();
		my @mess;
		while (my $mess=$out2->fetchrow_hashref){
			
			push(@mess,qq|<a href="$SCRIPT_NAME?ses=$PAR{ses}&reckey=$mess->{pk_mess}&act=mainbody&act2=newmess&account=$mess->{fk_account}">$mess->{subject}</a>|);
		}
		$output->{descr}=join "<BR>\n",@mess;
		if(@mess){
			$output->{delete_signature}=qq|<img src="content.cgi?get=image&mode=gif&f=sp" width="16" height="16" border="0">|;			
		}else{
			$output->{delete_signature}=qq|<a href="$SCRIPT_NAME?ses=$PAR{ses}&act=signatures&modify=delete&id=$output->{pk_signature}" onClick="return confirm('$LNG{SIGNATURE_DELETE_CONFIRM}')"><img src="content.cgi?get=image&mode=png&f=b_drop" width="16" height="16" border="0"></a>|;
		}
		$page->AddRow($output);
	}
	$page->ParseData;
	return $page->as_string;
}
sub print_signatures_pref{
	my $page=new hfparser
	DATA=>"$SHABL_DIR/manage_signatures.html",TO => "#end_account_pref",FROM=>"#start_account_pref";
	if($PAR{issubmit}){
		$PAR{name}=~s/^\s+//;
		$PAR{name}=~s/\s+$//;
		$page->set_error('name',"$LNG{ERROR_REQUIRED}") unless length($PAR{name});
		$page->set_error('name',"$LNG{SIGNATURE_INCORRECT_NAME}") if($PAR{name}=~/[^a-zA-Z0-9_]/);
		if($PAR{id}){
			$page->set_error('name',ucfirst("$LNG{ERROR_IS_ALREADY_EXISTS}")) if GetSQLCount("SELECT * FROM ${PREF}signatures WHERE name=? AND pk_signature<>?",$PAR{name},$PAR{id});
		}else{
			$page->set_error('name',ucfirst("$LNG{ERROR_IS_ALREADY_EXISTS}")) if GetSQLCount("SELECT * FROM ${PREF}signatures WHERE name=?",$PAR{name});
		}
		unless($page->is_error){
			if($PAR{id}){
				update_db("${PREF}signatures",{name=>$PAR{name},sig_text=>$PAR{sig_text},sig_html=>$PAR{sig_html}},{pk_signature=>$PAR{id}});
			}else{
				insert_db("${PREF}signatures",{name=>$PAR{name},sig_text=>$PAR{sig_text},sig_html=>$PAR{sig_html}});
			}
			print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}");
			exit;		
		}
	}
	unless($PAR{id}){
		$page->add_regesp('{ACTION_VALUE}',$LNG{SIGNATURE_NEW});
	}else{
		$page->add_regesp('{ACTION_VALUE}',$LNG{SIGNATURE_EDIT});
	}
	if($PAR{id}){
		my $hr=select_one_db("SELECT * FROM ${PREF}signatures WHERE pk_signature=?",$PAR{id});
		map{$page->set_def($_,$hr->{$_})}keys %$hr;
		my $sql2="SELECT * FROM ${PREF}mess WHERE mess LIKE ".$db->quote('%[SIGNATURE_'.$hr->{name}.']%')." OR messhtml LIKE ".$db->quote('%[SIGNATURE_'.$hr->{name}.']%')." ORDER by fk_account";
		if(GetSQLCount($sql2)){
			$page->Hide('<!--SHOW_IF_NEW-->');
			$page->add_regesp('{name}',$hr->{name});
			
		}else{
			$page->Hide('<!--SHOW_IF_EDIT-->');
		}
	}else{
		$page->Hide('<!--SHOW_IF_EDIT-->');

	}
	if($PAR{clone}){
		my $hr=select_one_db("SELECT * FROM ${PREF}signatures WHERE pk_signature=?",$PAR{clone});
		map{$page->set_def($_,$hr->{$_}) unless /name/}keys %$hr;
	}
	$page->ParseData;
	return $page->as_string;
}

sub print_manage_signatures{
	my %map;
	%map=(	""       =>\&print_signatures_report,
		pref  =>\&print_signatures_pref
	);
	$main_page=new dparser(
		DATA=>"$SHABL_DIR/main-settings.html"
	);
	#$main_page->add_regesp('{main_menu}',get_account_menu(\@SETTINGSMENU));
	$main_page->add_regesp('{main_menu}',"");
	my $func_ref;
	if ($map{$PAR{act2}}) {
		$func_ref=$map{$PAR{act2}};
	}else{
		$func_ref=sub{return $q->h1($LNG{INCORRECT_URL})}
	}
	$main_page->add_regesp('###TITLE###',$LNG{MANAGE_SIGNATURES});
	$main_page->add_regesp('{body}',&$func_ref);
	$main_page->ParseData;
	&printheader;
	$main_page->print;		
}
##################
sub add_menu_prospects{
my $page_ref=shift;
#my $menu;
#$menu=<<ALL__;
#<table width="100%" border="0" cellspacing="3" cellpadding="1">
#	<tr align="center" class="data"> 
#		<td><a href="$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=userform&account=$PAR{account}"><NOBR>$LNG{PROSPMENU_ADD_PROSP}</NOBR></a></td>
#		<td><a href="$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=import&account=$PAR{account}"><NOBR>$LNG{PROSPMENU_IMPORT}</NOBR></a></td>
#		<td><a href="$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=export&account=$PAR{account}"><NOBR>$LNG{PROSPMENU_EXPORT}</NOBR></a></td>
#		<td><a href="$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=loadfrom&account=$PAR{account}"><NOBR>$LNG{PROSPMENU_COPY}</NOBR></a></td>	
#		<td><a href="$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=bulk&account=$PAR{account}"><NOBR>$LNG{PROSPMENU_BULK_REMOVE}</NOBR></a></td>
#	</tr>
#</table>
#ALL__
$page_ref->add_regesp('{prospects_menu}',"");
}
##################
sub process_all{
	if ($ACT{$PAR{act}}){
		my $sub_ref=$ACT{$PAR{act}};
		&$sub_ref if $sub_ref;
	}else{
		printheader();
		print $q->start_html($LNG{ERROR});
		print $q->h1($LNG{ERROR_NOT_CHANGE_URL});
		print $q->end_html;
		exit;
	}
}
###################
sub get_account_menu{
	my $ref_menu=shift;
	my @MENU=@{$ref_menu};
	my $out;
	$out=$q->start_table({-border=>0,-align=>"center",width=>"100%"})."<TR>";
	my $count=@MENU;
	my $width=100/$count."%" if $count;
	my $menu;
	my $acct="";
	$acct='&account='.$PAR{account} if $PAR{account};
	my @menu=map{$q->td({-align=>center, -width=>$width},
				$q->a({-href=>"$SCRIPT_NAME?act=$PAR{act}&act2=".$_->{params}{act2}."&ses=$PAR{ses}".$acct,
						-target=>'_self', -class=>($PAR{act2} eq $_->{params}{act2}) ? 'menuACT' : 'menu'},"<NOBR>$_->{name}</NOBR>")
			)
		}@MENU;
	$out.=join "\n", @menu;
	$out.="</TR>".$q->end_table() ;	
	return $out;
}
########################################
sub get_full_menu{
	my $ref_menu=shift;
	my @MENU=@{$ref_menu};
	my $out;
	$out=<<ALL__;
<table  cellspacing="1" cellpadding="5"  border="0" align="center" width ="100%">
ALL__
	my $acct="";
	$acct='&account='.$PAR{account} if $PAR{account};
	foreach(@MENU){
		next unless ($_->{description});
		my $href=$q->a({-href=>"$SCRIPT_NAME?act=$PAR{act}&act2=".$_->{params}{act2}."&ses=$PAR{ses}".$acct,-target=>'_self'},qq|<img src="content.cgi?get=image&mode=gif&f=go" border="0" width="16" height="16">|);
		$out.=<<ALL__;
	<TR class="data">
                <td>$href</td>
                <td><STRONG>$_->{name}: </STRONG>$_->{description}</td>
              </tr>
ALL__
	}
	$out.=$q->end_table() ;	
	return $out;
}
##################
sub get_full_url{
	my $pars=shift;
	my %pars=%$pars;
	my $qq = new CGI;
	foreach (keys %pars){
		$qq->param($_,$pars{$_})
	}
	#-path_info=>1
	#-query=>1
	return $qq->url(-absolute=>1,-query=>1);
}

####################
#begin mapping functions
####################
#SETTINGS
sub print_settings_main{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	$page->SplitData("#begin#main","#end#main");
	$page->deleteBEFORE_AFTER();
	$page->add_regesp('{main_menu_body}',get_full_menu(\@SETTINGSMENU));
	$page->ParseData;
	return $page->as_string;
}
###################
sub print_settings_personal{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	my @set=qw(statbyemail adminname adminemail splashsettings);
	if ($PAR{issubmit}){
		$page->set_error("adminname",$LNG{ERROR_YOUR_NAME_REQUIRED}) unless $PAR{adminname};
		if ($PAR{adminemail}){
			$page->set_error("adminemail",$LNG{ERROR_EMAIL_INCORRECT}) unless checkemail($PAR{adminemail});
		}else{
			$page->set_error("adminemail",$LNG{ERROR_EMAIL_REQUIRED});
		}
	}
	if ($PAR{issubmit} && !$page->is_error){
		map{save_config(0,"$_",$PAR{$_})}@set;
		$page->add_regesp('{error}',"<h1 class=\"mess\">$LNG{MESS_SETTINGS_UPDATED}</h1>");
	}
	my @splval=qw(news daily_stats activity curbroadcast totalstat bounced bounced_total);
	map{$page->add_element('splashsettings',$_,$LNG{"SPLASH_PAGE_SETTINGS_".uc($_)})}@splval;
	
	my $sql="select * from ${PREF}account WHERE isact=1 ORDER by name";
	my $out=$db->prepare($sql);
	$out->execute();
	my %output;
	while ($output=$out->fetchrow_hashref){
		$page->add_element('splashsettings','account_'.$output->{pk_account},$LNG{ACCOUNT_BIG}." -> ".$output->{name});
	}
	map{$page->set_def("$_",$CONF{$_});}@set;
	$page->SplitData("#begin#personal","#end#personal");
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
###########################
sub print_settings_smtp{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	my @settings=qw(sendmail modsend smtp COUNT_PROC sendingdelay OLD_ALGORITHM_PROC smtpauth smtpusername smtppassword errorsto smtpuseadminemail smtpfromemail returnpath issendmailf sendmailaddress );
	if ($PAR{issubmit}){
		if ($PAR{modsend} eq ""){
			$page->set_error("modsend",$LNG{ERROR_NOT_SELECTED})
		}else{
			if ($PAR{modsend} eq 'sendmail'){
				unless ($PAR{sendmail}){
					$page->set_error("sendmail",$LNG{ERROR_REQUIRED_SENDMAIL}) 
				}else{
					if($PAR{sendmail}=~/[ ><;&]/){
						$page->set_error("sendmail",$LNG{ERROR_INCORRECT_SENDMAIL_PATH}) 
					}elsif(! -f $PAR{sendmail}){
						$page->set_error("sendmail",$LNG{ERROR_INCORRECT_SENDMAIL_NOT_EXISTS})
					}
					unless($page->is_error){
						if(length($PAR{errorsto})){
							$page->set_error("errorsto",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{errorsto}));				
						}
						if(length($PAR{returnpath})){
							$page->set_error("returnpath",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{returnpath}));				
						}
						if(length($PAR{issendmailf})){
							$page->set_error("sendmailaddress",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{sendmailaddress}));				
						}						
					}
				}
			}elsif($PAR{modsend} eq 'SMTP'){
				$page->set_error("smtp",$LNG{ERROR_REQUIRED_SMTP}) unless $PAR{smtp};
				if($PAR{smtpauth}){
					$page->set_error("smtpusername",$LNG{ERROR_REQUIRED}) unless length($PAR{smtpusername});
					$page->set_error("smtppassword",$LNG{ERROR_REQUIRED}) unless length($PAR{smtppassword});
				}
				if($PAR{smtpuseadminemail}){
					$page->set_error("smtpfromemail",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{smtpfromemail}));
				}
			}
		}
	}
	if ($PAR{issubmit} && !$page->is_error){
		map{save_config(0,$_,$PAR{$_})}@settings;
		$page->add_regesp('{error}',"<h1 class=\"mess\">$LNG{MESS_SETTINGS_UPDATED}</h1>");
	}
	if($CONF{modsend} eq 'SMTP'){
		$page->Hide('<!--HIDEIFSMTP-->');
	}else{
		$page->Hide('<!--HIDEIFSENDMAIL-->');
	}
	map{$page->add_element("COUNT_PROC",$_)}(1..10);
	map{$page->add_element("sendingdelay",$_)}(0..60);
	$page->set_def("sendingdelay",0);
	$page->add_element("modsend","","--select--");
	$page->add_element("modsend","sendmail");
	$page->add_element("modsend","SMTP");
	map{$page->set_def("$_",$CONF{$_})}@settings;
	$page->set_def("sendmailaddress",$CONF{adminemail}) unless length($CONF{sendmailaddress});
	$page->set_def("smtpfromemail",$CONF{adminemail}) unless length($CONF{smtpfromemail});
	$page->SplitData("#begin#smtp","#end#smtp");
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
#################
sub print_settings_timecorr{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	if ($PAR{issubmit}){
		if ($PAR{timecorr} ne ""){
			unless ($PAR{timecorr}=~m#^(\+|-)\d\d:\d\d$#){
				$page->set_error("timecorr",$LNG{ERROR_INCORRECT_FORMAT});
			}
		}
	}
	if ($PAR{issubmit} && !$page->is_error){
		save_config(0,"timecorr",$PAR{timecorr});
		save_config(0,'date_format',$PAR{date_format});
		$page->add_regesp('{error}',"<h1 class=\"mess\">$LNG{MESS_SETTINGS_UPDATED}</h1>");
		$CONF{timecorr}=$PAR{timecorr};
		$MY_TIME=time+TimeToSec($CONF{timecorr});
		$NOW=GetNow($PAR{timecorr});
		$db->do("UPDATE ${PREF}ses SET date=$NOW WHERE ran=?", undef, $PAR{ses});
	}
	$page->add_regesp('{time}',scalar(localtime()));
	$page->add_regesp('{mytime}',scalar(localtime($MY_TIME)));
	unless($CONF{date_format}){
		$CONF{date_format}='%m/%d/%Y';
	}
	eval{
		$page->add_regesp('{testdate}',strftime($CONF{date_format},localtime($MY_TIME)));
	};
	$page->add_regesp('{testdate}',qq|<FONT color=red>Error parsing format: $@</FONT>|) if $@;
	$page->set_def("date_format",$CONF{date_format});
	$page->set_def("timecorr",$CONF{timecorr});
	$page->SplitData("#begin#time","#end#time");
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
########################
sub print_settings_pass{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	if ($PAR{issubmit}){
		$page->set_error("oldpass",$LNG{ERROR_INCORRECT}) if ($PAR{oldpass} ne $CONF{adminpwd});
		if ($PAR{newpass1} && $PAR{newpass2}){
			$page->set_error("newpass1",$LNG{ERROR_NOT_EQUAL}) if ($PAR{newpass1} ne $PAR{newpass2});
			$page->set_error("newpass2",$LNG{ERROR_NOT_EQUAL}) if ($PAR{newpass1} ne $PAR{newpass2});
		}else{
			$page->set_error("newpass1",$LNG{ERROR_REQUIRED}) unless $PAR{newpass1};
			$page->set_error("newpass2",$LNG{ERROR_REQUIRED}) unless $PAR{newpass2};			
		}
	}
	if ($PAR{issubmit} && !$page->is_error){
		save_config(0,"adminpwd",$PAR{newpass1});
		$page->add_regesp('{error}',"<h1 class=\"mess\">$LNG{MESS_SETTINGS_UPDATED}</h1>"."<A href=\"$SCRIPT_NAME\" target=\"parent\">$LNG{MESS_LOGOUT_TO_CHECK}</a>");
	}

	$page->SplitData("#begin#pass","#end#pass");
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
#############Backup
sub get_dir_size{
my $dir=shift;
my $dirsize=0;
if (-d "$dir"){
	my @files;
	opendir(DIR,$dir) || die $LNG{ERROR_CANT_OPEN_DIR};
	while (my $file=readdir(DIR)){
		next if ($file=~/^\.+$/);
		push (@files,$file);
	}
	closedir(DIR);
	foreach my $file(@files){
		if(-d "$dir/$file"){
			$dirsize += get_dir_size("$dir/$file");
		}else{
			$dirsize += (stat("$dir/$file"))[7];
		}
	}
}elsif(-f $dir){
	return (stat("$dir"))[7];
}
return $dirsize;
}
###################
sub remove_dir{
my $dir=shift;
if (-d "$dir"){
	opendir(DIR,$dir) || die $LNG{ERROR_CANT_OPEN_DIR};
	my @files;
	while (my $file=readdir(DIR)){
		next if ($file=~/^\.+$/);
		push (@files,$file);

	}
	closedir(DIR);
	foreach my $file(@files){
		if(-d "$dir/$file"){
			remove_dir("$dir/$file");
		}else{
			unlink("$dir/$file") || die "$LNG{ERROR_CANT_UNLINK_FILE} $dir/$file";
		}
	}
}
rmdir($dir);
}
sub create_backup{
	my $name=shift;
	unless (-d $glbackupdir){
		mkdir($glbackupdir,0777) || die "${ERROR_CANT_CREATE_DIR} $glbackupdir : $!";
	}
	my @tables=map{"${PREF}$_"}@backup_tables;
	return if ($name=~/[^a-zA-Z0-9_-]/);
	my $dirstore="$glbackupdir/$name";
	remove_dir($dirstore) if (-d $dirstore);
	mkdir($dirstore,0777) || die "${ERROR_CANT_CREATE_DIR} $dirstore : $!";
	my $path;
	if($ENV{PATH_TRANSLATED}){ 
		$path="$ENV{PATH_TRANSLATED}";
	}elsif($ENV{SCRIPT_FILENAME}){
		$path="$ENV{SCRIPT_FILENAME}";
	}
	my $delm;
	$delm='/' if $path=~/\//;
	$delm='\\' if $path=~/\\/;
	my @path=split(/\/|\\/,$path);
	$path=join($delm, @path[0..@path-2]);
	foreach $table(@tables){
		my $filename="$path${delm}$glbackupdir${delm}$name${delm}$table.dmp"; 
		open (FILE,">$filename") || die "$LNG{ERROR_CANT_OPEN_FILE} $filename $LNG{ERROR_CANT_WRITE}";
		my $sql="SHOW fields FROM $table";
		my $out=$db->prepare($sql);
		$out->execute();
		my @cols;
		while (my @output=@{$out->fetchrow_arrayref}){
			push (@cols,$output[0]);
		}
		print FILE join("\t",@cols)."\n";
		my $sql="SELECT * from $table";
		my $out=$db->prepare($sql);
		$out->execute();
		while (my %output=%{$out->fetchrow_hashref}){
			@output=map{$db->quote($output{$_})}@cols;
			#map{s/\t/\\t/g}@output;
			print FILE join(", ",@output)."\n";
		}
		close(FILE);
	}
	unless ($^O=~/win/i){
		#Linux
		chdir($glbackupdir);
		`tar -cf $name.tar $name`;
		`gzip $name.tar`;
		chdir("..");
		remove_dir("$glbackupdir/$name");
	}else{
		
	}
}
sub LoadTableFromFile{
	my($table,$file)=@_;
	unless(open (FILE,$file)){
		die ("$LNG{ERROR_CANT_OPEN_FILE} : $! ");
		return;
	}
	$db->do("DELETE FROM $table");
	unless($file=~/attach/){
	#	local $/="\n";
		my $cols=<FILE>;
		chomp($cols);
		my @cols=split(/\t/,$cols);
		$cols=join(", ",@cols);
		while (<FILE>){
			chomp;
			$sql="INSERT INTO $table ($cols) VALUES ($_)";
			$db->do($sql);

		}
	}else{
		binmode(FILE);
		my $buff,$data;
		while (read(FILE,$buff,8*2**10)){
			$data.=$buff;
		}
		my @lines=split(/\n/,$data);
		$data="";
		$buff="";
		my @cols=split(/\t/,shift(@lines));
		foreach(@lines){
			$sql="INSERT INTO $table ($cols) VALUES ($_)";
			$db->do($sql);
		}
	}
	close(FILE);
}
sub print_settings_backup{
	my $page = new hfparser(
		DATA=>$settings_shabl,
		ERROR_AFTER_INPUT=>0
	);
	my @tables=map{"${PREF}$_"}@backup_tables;
	if ($PAR{issubmit}=1){
		if ($PAR{backup}){
			if($PAR{filename}=~/[^a-zA-Z0-9_-]/){
				$page->set_error('filename', $LNG{ERROR_FILENAME_INCORRECT});
			}
			if(length($PAR{filename})<4){
				$page->set_error('filename', $LNG{ERROR_SHORTER_THEN_3});
			}

			unless ($page->is_error()){
				create_backup($PAR{filename});
			}
		}
		if ($PAR{'unlink'}){
			my @files=$q->param("unlinkcheck");
			foreach my $file(@files){
				next if($file=~/[^a-zA-Z0-9_-]/);
				my $filename="$glbackupdir/$file";
				remove_dir($filename) if (-d $filename);
				unless ($^O=~/win/i){
					$filename=$filename.'.tar.gz';
					unlink($filename) || die ("$LNG{ERROR_CANT_UNLINK_FILE} $filename $!");
				}
			}

		}
		if ($PAR{'restore'}){
			if($PAR{rest}){
				chdir($glbackupdir);
				my $backup=$PAR{rest};
				unless($^O=~/win/i){
					`gunzip < $backup.tar.gz | tar xvf -` if (-f "$backup.tar.gz");
					unless (-d $backup){
						$page->set_error('none',"Files was not unpacked from $backup.tar.gz");
					}
				}
				foreach my $table(@tables){
					$page->set_error($table, "The file $table.dmp is not exist on backup directory $backup probably table prefix was changed.") unless (-f "$backup/$table.dmp");
				}
				unless ($page->is_error()){
					$page->add_regesp("{error}",qq{<h1 class="mess">Database was restored from backup - $backup</h1>});
					my $path;
					if($ENV{PATH_TRANSLATED}){ 
						$path="$ENV{PATH_TRANSLATED}";
				 	}elsif($ENV{SCRIPT_FILENAME}){
						$path="$ENV{SCRIPT_FILENAME}";
					}
					my $delm;
					$delm='/' if $path=~/\//;
					$delm='\\' if $path=~/\\/;
					my @path=split(/\/|\\/,$path);
					$path=join($delm, @path[0..@path-2]);
					#my $path=$ENV{SCRIPT_FILENAME};
					#my @path=split(/\//,$path);
					#$path=join("\/", @path[0..@path-2]);
					foreach $table(@tables){
						#next unless (-f "$backup/$table.dmp");
						my $filename="$path${delm}$glbackupdir${delm}$backup${delm}$table.dmp"; 
						LoadTableFromFile($table,$filename);
					}
					save_config(0,"adminpwd",$CONF{adminpwd});
					unless ($^O=~/win/i){
						remove_dir("$backup");
					}					
				}
				chdir('..');				
			}
		}
	}
	opendir(DIR,$glbackupdir);
	my @backups;
	while(my $file=readdir(DIR)){
		next if ($file=~/^\.+$/);
		unless ($^O=~/win/i){
			if ($file=~/(.*)\.tar\.gz/){
				push(@backups,$1);
			}
		}else{
			if (-d "$glbackupdir/$file"){
				push(@backups,$file);
			}
		}
	}
	my $BACKUP="";
	foreach my $name(@backups){
		my $filename="$glbackupdir/$name";
		$filename=$filename.'.tar.gz' unless ($^O=~/win/i);
		my($dev,$ino,$mode,$nlink,$uid,$gid,$rdev,$size, $atime,$mtime,$ctime,$blksize,$blocks)= stat $filename;
		my $time=localtime($ctime);
		if ($^O=~/win/i){
			$size=get_dir_size("$glbackupdir/$name");
		}
		$BACKUP.=<<ALL__;
                      <tr class="data"> 
                        <td width="7%" align="center"><INPUT type="checkbox" name="unlinkcheck" value="$name"></td>
                        <td width="30%" align="center">$name</td>
                        <td width="6%" align="center"><INPUT type="radio" name="rest" value="$name"></td>
                        <td width="24%" align="center"><NOBR>$time</NOBR></td>
                        <td width="33%" align="center">$size</td>
                      </tr>
ALL__

	}
	$page->add_regesp('{BACKUP}',$BACKUP);
	$page->SplitData("#begin#backup","#end#backup");
	$page->deleteBEFORE_AFTER();
	unless($BACKUP){
		$page->SplitData("<!--HIDE_START-->","<!--HIDE_END-->");
		$page->replaceINSIDE("");
	}
#$page->add_regesp("{mess_hour}",sprintf("%4d",$PAR{messcount}/$sec*60*60));				
	$page->ParseData;		
	return $page->as_string;		
}
#############Backup
################
sub print_settings_test{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	$page->add_regesp("{conf_mail}",$CONF{modsend});			
	if ($PAR{issubmit}){
		unless($PAR{emailtest}){
			$page->set_error("emailtest",$LNG{ERROR_REQUIRED});
		}else{
			unless(checkemail($PAR{emailtest})){
				$page->set_error("emailtest",$LNG{ERROR_EMAIL_INCORRECT});				
			}
		}
		unless($PAR{messcount}){
			$page->set_error("messcount",$LNG{ERROR_REQUIRED});
		}else{
			if ($PAR{messcount}=~/[^0-9]/){
				$page->set_error("messcount","digits only");
			}elsif($PAR{messcount}>300){
				$page->set_error("messcount","300 is maximum");
			}elsif($PAR{messcount}<30){
				$page->set_error("messcount","30 is minimum");
			}
		}
	}
	if ($PAR{issubmit} && !$page->is_error()){
		my $starttime=time();
		my $DATA=<<ALL__;

This is a performance test message.

  $ENV{SERVER_ADMIN}
  $ENV{HTTP_HOST}
  $ENV{REMOTE_ADDR}
ALL__
		
		$msg = new MIME::Lite 
			From    =>"$CONF{adminname} <$CONF{adminemail}>",
			To      =>" <$PAR{emailtest}>",
			Subject =>"Performance test message",
			Data    =>$DATA;

		foreach(1..$PAR{messcount}){
			MIMEsendto($PAR{emailtest},$msg);
		}
		my $endtime=time();
		my $sec=$endtime-$starttime;
		$sec=1 unless $sec;
		$page->SplitData("#begin#testresult","#end#testresult");
		$page->deleteBEFORE_AFTER();
		$page->add_regesp("{messcount}",$PAR{messcount});
		$page->add_regesp("{emailtest}",$PAR{emailtest});		
		$page->add_regesp("{seconds}",$sec);
		$page->add_regesp("{mess_sec}",sprintf("%4d",$PAR{messcount}/$sec));
		$page->add_regesp("{mess_min}",sprintf("%4d",$PAR{messcount}/$sec*60));		
		$page->add_regesp("{mess_hour}",sprintf("%4d",$PAR{messcount}/$sec*60*60));				
		$page->ParseData;		
		return $page->as_string;		
		
	}else{
		$page->SplitData("#begin#test","#end#test");
		$page->deleteBEFORE_AFTER();
		$page->set_def("emailtest",$CONF{adminemail});		
		$page->set_input("messcount",{size=>3,maxlength=>3});
		$page->set_def("messcount",50);
		$page->ParseData;
		return $page->as_string;
	}
}
################
sub print_settings_log{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	$page->SplitData("#begin#log","#end#log");
	$page->deleteBEFORE_AFTER();
	if ($PAR{issubmit}){
		save_config(0,"enablelog",$PAR{enablelog});
		if($PAR{cleanall}){
			$db->do("DELETE FROM ${PREF}log");
			&Error;
		}
		if($PAR{cleandate}){
			my $WHERE="WHERE date BETWEEN ".$db->quote("$PAR{year1}-$PAR{month1}-$PAR{day1}")." AND DATE_ADD(".$db->quote("$PAR{year2}-$PAR{month2}-$PAR{day2}").", INTERVAL 1 DAY)";
			$db->do("DELETE FROM ${PREF}log $WHERE");
			&Error;
		}
	}
	#DATE
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($MY_TIME);
	$year+=1900;$mon++;
	foreach (1..31){
		my $dd=sprintf("%02d",$_);
		$page->add_element("day1",$_,$dd);
		$page->add_element("day2",$_,$dd)
	}
	$page->set_def("day1",$mday);	$page->set_def("day2",$mday);
	my @month=($LNG{MONTH_1},$LNG{MONTH_2},$LNG{MONTH_3},$LNG{MONTH_4},$LNG{MONTH_5},$LNG{MONTH_6},$LNG{MONTH_7},$LNG{MONTH_8},$LNG{MONTH_9},$LNG{MONTH_10},$LNG{MONTH_11},$LNG{MONTH_12});
	foreach (1..12){
		$page->add_element("month1",$_,$month[$_-1]);$page->add_element("month2",$_,$month[$_-1]);
	}
	$page->set_def("month1",$mon);	$page->set_def("month2",$mon);
	foreach (2002..$year){
		$page->add_element("year1",$_);
		$page->add_element("year2",$_);
	}
	$page->set_def("year1",$year);	$page->set_def("year2",$year);
	#END DATE
	$page->set_def("enablelog",$CONF{enablelog});
	my @WHERE=();
	if ($PAR{issubmit}){
		if ($PAR{usedate}){
			push(@WHERE,"date BETWEEN ".$db->quote("$PAR{year1}-$PAR{month1}-$PAR{day1}")." AND DATE_ADD(".$db->quote("$PAR{year2}-$PAR{month2}-$PAR{day2}").", INTERVAL 1 DAY)");
		}
	}else{
		push(@WHERE,"date BETWEEN '$year-$mon-$mday' AND DATE_ADD('$year-$mon-$mday', INTERVAL 1 DAY)");
	}
	my $WHERE=join(" AND ",@WHERE);
	$WHERE="WHERE ".$WHERE if $WHERE;
	my $logdata;
	my $sql="SELECT * FROM ${PREF}log $WHERE ORDER by pk_log ASC";
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	unless ($out->rows()){
		$logdata.=<<ALL__;
                <tr class="data"> 
                  <td align="center" class="data" colspan=2><b>No logs found</b></td>
                </tr>
ALL__
	}
	while (my %output=%{$out->fetchrow_hashref}){
		$logdata.=<<ALL__;
                <tr class="data"> 
                  <td width="15%" align="right" class="data"><b><NOBR>$output{date}</NOBR></b></td>
                  <td width="54%" align="left">${\&sequre($output{log})}</td>
                </tr>
ALL__
	}
	
	$page->add_regesp('{allcountlog}',GetSQLCount("SELECT * FROM ${PREF}log"));
	$page->add_regesp('{logdata}',$logdata);
	$page->ParseData;
	return $page->as_string;
}
################
sub print_settings{
	my %map;
	%map=(	""       =>\&print_settings_main,
		personal  =>\&print_settings_personal,
		smtp     =>\&print_settings_smtp,
		pass     =>\&print_settings_pass,
		timecorr    =>\&print_settings_timecorr,
		test    =>\&print_settings_test,
		backup    =>\&print_settings_backup

	);
	$main_page=new dparser(
		DATA=>"$SHABL_DIR/main-settings.html"
	);
	$main_page->add_regesp('{main_menu}',get_account_menu(\@SETTINGSMENU));
	my $func_ref;
	if ($map{$PAR{act2}}) {
		$func_ref=$map{$PAR{act2}};
	}else{
		$func_ref=sub{return $q->h1($LNG{INCORRECT_URL})}
	}
	$main_page->add_regesp('###TITLE###',$LNG{GLOBAL_SETTS});
	$main_page->add_regesp('{body}',&$func_ref);
	$main_page->ParseData;
	&printheader;
	$main_page->print;	
}
################
##STAT
##############
sub print_stat_main{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	$page->SplitData("#begin#main","#end#main");
	$page->deleteBEFORE_AFTER();
	$page->add_regesp('{main_menu_body}',get_full_menu(\@STATMENU));
	$page->ParseData;
	return $page->as_string;
}
sub print_stat_curlog{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	$page->SplitData("#begin#broadcastlog","#end#broadcastlog");
	$page->deleteBEFORE_AFTER();
	$page->add_regesp('{mess}',"");
	$page->add_regesp('{broadcast_file}',$BroadcastLogFile);
	$page->add_regesp('{count_rows}',GetSQLCount("SELECT * FROM ${PREF}brodcastlog"));
	if($PAR{issubmit}){
		if($PAR{save_broadcast_log}){
			if(open(FILE,">>$BroadcastLogFile")){
				unless ($^O=~/win/i){
					unless(flock(FILE, LOCK_EX())){
						$page->set_error("save_broadcast_log", "$LNG{ERROR_CANT_LOCK_FILE} ".LOCK_EX()." $!\n");
						close(FILE);
						
					}else{
						print FILE "Broadcast logging starts at ".GetDate()."\n";
						print FILE "TIME\tPROCESS NUMBER\tPID\tSTATUS MESSAGE\n";
						close(FILE);
					}				
				}else{
						print FILE "Broadcast logging starts at ".GetDate()."\n";
						print FILE "TIME\tPROCESS NUMBER\tPID\tSTATUS MESSAGE\n";
						close(FILE);
				}
			}else{
				$page->set_error("save_broadcast_log", "$LNG{ERROR_CANT_OPEN_FILE} $BroadcastLogFile $LNG{ERROR_CANT_WRITE} ($!) <BR> $LNG{ERROR_NEED_TO_CREATE} $BroadcastLogFile $LNG{ERROR_NEED_TO_CREATE2}");
			}
		}
		unless($page->is_error){
			$page->add_regesp('{mess}',"<H1 class=mess>$LNG{MESS_SETTINGS_UPDATED}</H1>");				
			save_config(0,"save_broadcast_log",$PAR{save_broadcast_log});
		}
	}
	$page->set_def("save_broadcast_log",$CONF{save_broadcast_log});	
	my $mess = "";
	my $sql="SELECT DATE_FORMAT(date, '%Y-%b-%d &nbsp;&nbsp; %H:%i:%S' ) as datelog, pid,log,procnomber FROM  `${PREF}brodcastlog` ORDER by `date` ASC";
	my $out=$db->prepare($sql);
	$out->execute;
	&Error;
	unless($out->rows()){
		$mess.=qq|<h1 class="mess"> $LNG{MESS_NO_BROADCAST_LOG}</h1>|;
	}else{
		my $count=$out->rows();
		$mess.=<<ALL__;
<table border="0" align="center" width="70%" cellspacing="1" cellpadding="2">
 <tr class="dataheader"> 
 <td width="5%"><NOBR>$LNG{BROADCAST_LOG_PROC}</NOBR></td>
 <td width="10%"><NOBR>PID</NOBR></td>
 <td width="20%"><NOBR>$LNG{BROADCAST_LOG_TIME}</NOBR></td>
 <td width="65%"><NOBR>$LNG{BROADCAST_LOG_STATUS}</NOBR></td>
</tr>
ALL__
		while (my $output=$out->fetchrow_hashref){
			$output->{procnomber}="<B>$LNG{BROADCAST_LOG_MAIN}</B>" unless $output->{procnomber};
				$mess.=<<ALL__;
 <tr class="data"> 
 <td width="5%" align=center>$output->{procnomber}</td>
 <td width="10%" align=center><B>$output->{pid}</B></td>
 <td width="20%"><NOBR>$output->{datelog}</NOBR></td>
 <td width="65%">$output->{log}</td>
</tr>
ALL__
		}
		$mess.="</table>";	
	}
	$page->add_regesp('{broadcast_mess}',$mess);
	$page->ParseData;
	return $page->as_string;	
}
sub set_leng{
	my $out=<<ALL__;
<table width="100%" border="0" cellspacing="0" cellpadding="0" height="80%">
  <tr>
    <td valign="middle">
<form name="form1" method="POST" action="{ME}" target="_top">
  {error}{fm_hidden_ses}{fm_hidden_act} 
  <input type="hidden" name="issubmit" value="1">
  <table width="50%" border="0" cellspacing="3" cellpadding="4" align="center">
    <tr class="dataheader"> 
      <td colspan="2"><b>[LNG_LANG_SELECT_LANG_TABHEADER]</b></td>
    </tr>
    <tr class="data"> 
      <td width="48%" align="right" class="data"><b>[LNG_LANG_LANG]:</b></td>
      <td width="52%"><div align="left">{fm_select_langnow}</div></td>
    </tr>
    <tr class="data" align="center"> 
      <td colspan="2"> 
      <input type="submit" value="Save lang" class="BUTTONmy" name="submit">
      </td>
    </tr>
  </table>
</form></td></tr></table>
ALL__
	if($PAR{issubmit} and $PAR{langnow}){
		save_config(0,'langnow',$PAR{langnow});
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}");
		exit;
	}
	my $page=new hfparser(
		IS_CRIPT=>0,
		SOURCE=>'string',
		DATA=>$out
	);
#	my @files=<"shabl/lang/*.txt">;
	my $lang_dir='shabl/lang';
	opendir(DIR,$lang_dir);
	my @backups;
	while(my $file=readdir(DIR)){
		next unless $file=~/\.txt$/;
		$file=~s/\.txt$//;
		open(FILE,"$lang_dir/$file.txt");
		my $fline=<FILE>;
		close(FILE);
		chomp($fline);
		my ($lang_name,$lengencod)=split(/\t/,$fline);
		$page->add_element('langnow',$file,"$lang_name ($lengencod)");
	}
	closedir(DIR);
	$page->set_def('langnow',$CONF{langnow});
	$page->ParseData;
	return $page->as_string;
	
}
#################
sub print_set_leng{
	$main_page=new dparser(
		DATA=>"$SHABL_DIR/main-settings.html"
	);
	$main_page->add_regesp('###TITLE###',$LNG{LANG_SELECT_LANG});
	$main_page->add_regesp('{body}',set_leng());
	$main_page->add_regesp('{main_menu}',"");
	$main_page->ParseData;
	&printheader;
	$main_page->print;
		
}
#################
sub print_stat{
	my %map;
	%map=(	""       =>\&print_stat_main,
		curlog  =>\&print_stat_curlog,
		'log'    =>\&print_settings_log,
		total    =>\&print_stat_total,
	);
	$main_page=new dparser(
		DATA=>"$SHABL_DIR/main-settings.html"
	);
	my $func_ref;
	if ($map{$PAR{act2}}) {
		$func_ref=$map{$PAR{act2}};
	}else{
		$func_ref=sub{return $q->h1($LNG{ERROR_NOT_CHANGE_URL})}
	}
	$main_page->add_regesp('###TITLE###',$LNG{STAT_STATISTICS});
	$main_page->add_regesp('{body}',&$func_ref);
	$main_page->add_regesp('{main_menu}',
		get_hor_menu(\@STATMENU,{ses=>$PAR{ses},act=>$PAR{act}},[['menu','menuACT'],['menu2','menu2ACT']])
		);
	$main_page->ParseData;
	&printheader;
	$main_page->print;	
}

sub print_stat_account{
	my $page=shift;
	$page->add_regesp('{log_header}',$LNG{STAT_TOTAL_PROSP});
	$page->Hide("<!--HIDE_PERIOD-->");
	my $sql="select * from ${PREF}account";
	my $out=$db->prepare($sql);
	$out->execute();
	my %accountname;
	while (my %output=%{$out->fetchrow_hashref}){
		$accountname{$output{pk_account}}=$output{name};
	}
	my $Total_act,$Total_inact;
my $logdata.=<<ALL__;
<table border="0" align="center" width="60%" cellspacing="1" cellpadding="2">
 <tr class="dataheader"> 
 <td >$LNG{STAT_ACCOUNT}</td>
 <td >$LNG{STAT_ACT_PROSP}</td>
 <td >$LNG{STAT_INACT_PROSP}</td>
 <td >$LNG{STAT_TOTAL}</td>
</tr>
ALL__
	foreach my $account_id(sort {$accountname{$a} cmp $accountname{$b}}keys %accountname){
		my $total_activ   = GetSQLCount("Select * from ${PREF}user WHERE fk_account=? AND  isact=1",$account_id);
		my $total_inactiv = GetSQLCount("Select * from ${PREF}user WHERE fk_account=? AND  isact<>1",$account_id);
		my $total=$total_activ+$total_inactiv;
		$Total_act+=$total_activ;
		$Total_inact+=$total_inactiv;
		$logdata.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><a href="$SCRIPT_NAME?act=mainbody&account=$account_id&ses=$PAR{ses}">$accountname{$account_id}</a></td>
 <td >$total_activ</td>
 <td >$total_inactiv</td>
 <td >$total</td>
</tr>	
ALL__
		
	}
	my $tot=$Total_inact+$Total_act;
	$logdata.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><b>$LNG{STAT_TOTAL}:</b></td>
 <td ><b>$Total_act</b></td>
 <td ><b>$Total_inact</b></td>
 <td ><b>$tot</b></td>
</tr>	
</table>
ALL__
 $logdata.=get_gif_link();
	$page->add_regesp('{logdata}',$logdata);
	$page->ParseData;
	return $page->as_string;
}
sub get_gif_link{
	my $script=$SCRIPT_NAME;
	my @chars=('a'..'z','A'..'Z',0..9,'_');
	my $ran=join("", @chars[map{rand @chars}(1..8)]);
	$script=~s/responder\.cgi/logpng.cgi/;
	$script.="?rn=$ran&".join("&",map{"$_=$PAR{$_}"}keys %PAR);
	return qq|<DIV align="center"><IMG src="$script" hspace="5" vspace="5" alt="Diagram"></DIV>|;
}
sub print_stat_total{
	my $page = new hfparser(
		DATA=>$settings_shabl		
	);
	$page->SplitData("#begin#total","#end#total");
	$page->deleteBEFORE_AFTER();
	if ($PAR{modelog} eq 'account'){
		return print_stat_account($page);
	}
	#DATE
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($MY_TIME);
	$year+=1900;$mon++;
	$PAR{year1}=$year unless $PAR{year1};
	$PAR{year2}=$year unless $PAR{year2};
	$PAR{month1}=$mon unless $PAR{month1};
	$PAR{month2}=$mon unless $PAR{month2};
	$PAR{day1}=$mday unless $PAR{day1};
	$PAR{day2}=$mday unless $PAR{day2};
	foreach (1..31){
		my $dd=sprintf("%02d",$_);
		$page->add_element("day1",$_,$dd);
		$page->add_element("day2",$_,$dd)
	}
	$page->set_def("day1",$PAR{day1});
	$page->set_def("day2",$PAR{day2});
	my @month=($LNG{MONTH_1},$LNG{MONTH_2},$LNG{MONTH_3},$LNG{MONTH_4},$LNG{MONTH_5},$LNG{MONTH_6},$LNG{MONTH_7},$LNG{MONTH_8},$LNG{MONTH_9},$LNG{MONTH_10},$LNG{MONTH_11},$LNG{MONTH_12});
	foreach (1..12){
		$page->add_element("month1",$_,$month[$_-1]);$page->add_element("month2",$_,$month[$_-1]);
	}
	$page->set_def("month1",$PAR{month1});
	$page->set_def("month2",$PAR{month2});
	foreach (2002..$year){
		$page->add_element("year1",$_);
		$page->add_element("year2",$_);
	}
	$page->set_def("year1",$PAR{year1});
	$page->set_def("year2",$PAR{year2});
	#END DATE
	$page->set_def("enablelog",$CONF{enablelog});
	my @WHERE=();
	push @WHERE, "`date` >=".$db->quote("$PAR{year1}-$PAR{month1}-$PAR{day1}");
	push @WHERE, "`date` <=".$db->quote("$PAR{year2}-$PAR{month2}-$PAR{day2}");	
	my $WHERE=join(" AND ",@WHERE);
	$WHERE="WHERE ".$WHERE if $WHERE;
	my $logdata;
	my $sql=<<ALL__;
SELECT  `name`,`pk_account` ,    
SUM(`subscribers`) as subscribers ,  
SUM(`unsubscribers`) as unsubscribers,
SUM(`sent_manual`) as `sent_manual`,
SUM(`sent_sheduled`) as `sent_sheduled`,
SUM(`sent_sequential`) as `sent_sequential` ,
SUM(`sent_subscribe`) as `sent_subscribe`,
SUM(`sent_unsubscribe`) as `sent_unsubscribe` ,
SUM(`sent_doubleoptin`) as `sent_doubleoptin` ,
SUM(`sent_manual`)+SUM(`sent_sheduled`)+SUM(`sent_sequential`)+SUM(`sent_subscribe`)+SUM(`sent_unsubscribe`) as total_sent,
SUM(`subscribers`)-SUM(`unsubscribers`) as  total_subscribers
FROM  `${PREF}stat_account_dayly` 
RIGHT JOIN ${PREF}account ON pk_account=fk_account
$WHERE 
GROUP BY fk_account
ALL__
unless($PAR{modelog}){
$sql.=" HAVING total_sent<>0 ORDER by total_sent DESC ";
}else{
$sql.=" HAVING subscribers<>0 OR unsubscribers<>0 ORDER by total_subscribers DESC";
}
	
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	unless ($out->rows()){
		$logdata.=<<ALL__;
		<H1 class=mess>$LNG{STAT_NO_LOGS_FOUND}</H1>
ALL__
	}else{
		unless($PAR{modelog}){
$logdata.=<<ALL__;
<table border="0" align="center" width="100%" cellspacing="1" cellpadding="2">
 <tr class="dataheader"> 
 <td ><NOBR>$LNG{STAT_ACCOUNT}</NOBR></td>
 <td >$LNG{STAT_SEQUNTIAL}</td>
 <td >$LNG{STAT_SHEDULED}</td>
 <td >$LNG{STAT_MANUAL}</td>
 <td ><NOBR>$LNG{STAT_DOI}</NOBR></td>
 <td >$LNG{STAT_SUBSCRIBE}</td>
 <td >$LNG{STAT_UNSUBSCRIBE}</td>
 <td >$LNG{STAT_TOTAL}</td>
</tr>
ALL__
		}else{
$logdata.=<<ALL__;
<table border="0" align="center" width="50%" cellspacing="1" cellpadding="2">
 <tr class="dataheader"> 
 <td >$LNG{STAT_ACCOUNT}</td>
 <td >$LNG{STAT_SUBSCRIBERS}</td>
 <td >$LNG{STAT_UNSUBSCRIBERS}</td>
 <td >$LNG{STAT_TOTAL}</td>
</tr>
ALL__
		}
		
		my %itog;
		
		while (my $output=$out->fetchrow_hashref){
			map{$itog{$_}=$itog{$_}+$output->{$_} unless(/account|name/)}keys %{$output};
			unless($PAR{modelog}){
			$logdata.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><a href="$SCRIPT_NAME?act=mainbody&account=$output->{pk_account}&ses=$PAR{ses}">$output->{name}</a></td>
 <td >$output->{sent_sequential}</td>
 <td >$output->{sent_sheduled}</td>
 <td >$output->{sent_manual}</td>
 <td >$output->{sent_doubleoptin}</td>
 <td >$output->{sent_subscribe}</td>
 <td >$output->{sent_unsubscribe}</td>
 <td >$output->{total_sent}</td>
</tr>
ALL__
			}else{
			$logdata.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><a href="$SCRIPT_NAME?act=mainbody&account=$output->{pk_account}&ses=$PAR{ses}">$output->{name}</a></td>
 <td >$output->{subscribers}</td>
 <td >$output->{unsubscribers}</td>
 <td >$output->{total_subscribers}</td>
</tr>
ALL__
			}
		}
			unless($PAR{modelog}){
			$logdata.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><b>$LNG{STAT_TOTAL}</b></td>
 <td ><b>$itog{sent_sequential}</b></td>
 <td ><b>$itog{sent_sheduled}</b></td>
 <td ><b>$itog{sent_manual}</b></td>
 <td ><b>$itog{sent_doubleoptin}</b></td>
 <td ><b>$itog{sent_subscribe}</b></td>
 <td ><b>$itog{sent_unsubscribe}</b></td>
 <td ><b>$itog{total_sent}</b></td>
</tr>	
</table>
ALL__
		}else{
			$logdata.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><b>$LNG{STAT_TOTAL}</b></td>
 <td ><b>$itog{subscribers}</b></td>
 <td ><b>$itog{unsubscribers}</b></td>
 <td ><b>$itog{total_subscribers}</b></td>
</tr>	
</table>
ALL__
		}
$logdata.=get_gif_link();
}
	my $header;
	my $m1=$month[$PAR{month1}-1];
	my $m2=$month[$PAR{month2}-1];
	my $period;
	if ($m1 eq $m2 && $PAR{day1} == $PAR{day2} && $PAR{year1}==$PAR{year2}){
		$period = "$LNG{STAT_PERIOD_FOR} $PAR{day1} $m1 $PAR{year1}";
	}else{
		$period = "$LNG{STAT_PERIOD_FROM} $PAR{day1} $m1 $PAR{year1} $LNG{STAT_PERIOD_TILL} $PAR{day2} $m2 $PAR{year2}";
	}
	
	unless($PAR{modelog}){
		$header="$LNG{STAT_SENT_MESS_STAT} $period";
	}else{
		$header="$LNG{STAT_SUBSCRIBERS_STAT} $period";
	}
	$page->add_regesp('{log_header}',"$header");
	$page->add_regesp('{logdata}',$logdata);
	$page->ParseData;
	return $page->as_string;
}
#################
#################
##ACCOUNT
#################
#################
#USERS
#################
sub print_user_form{
	local @FIELDS;
	@FIELDS=load_account_fields($PAR{account});
	my $page = new hfparser(
		DATA=>$main_shabl,
		FROM=>'#begin#user_form',TO=>'#end#user_form'
	);	
	if ($PAR{issubmit}){
		#SET ERROR
		
		$page->set_error("email",$LNG{ERROR_EMAIL_INCORRECT}) unless checkemail($PAR{email});
	        $page->set_error("email","$LNG{TXT_EMAIL_ADDRESS} <B>$PAR{email}</b>  $LNG{ERROR_IS_ALREADY_EXISTS}")		
		  if GetSQLCount("SELECT * from ${PREF}user where fk_account=? AND email=? AND pk_user<>?",$PAR{account},$PAR{email},$PAR{reckey});
		if($PAR{fk_affiliate}){
			$page->set_error("fk_affiliate", $LNG{PROSPECT_NOT_FOUND}) unless GetSQLCount("SELECT * FROM ${PREF}user WHERE pk_user=? and fk_account=?",$PAR{fk_affiliate},$PAR{account});
		}
		unless($page->is_error){
			if($CONF{useblacklist}){
				$page->set_error("email",$CONF{blacklist_error}) if GetSQLCount("SELECT * FROM ${PREF}bounce_banemails WHERE email=?",$PAR{email});
			}
	  	}
	      	if(length($PAR{fromemail})){
			$page->set_error('fromemail',$LNG{ERROR_EMAIL_INCORRECT}) unless checkemail($PAR{fromemail});
		}
		map{
			if(length($PAR{$_})){
				unless($PAR{$_}=~/\d\d\d\d-\d\d-\d\d/){
					$page->set_error("$_",$LNG{ERROR_INCORRECT})
				}
			}		
		}qw(datereg datelastsend);
	
		unless($page->is_error){
			my $last;
			my $datelastsend;					
			if($PAR{datelastsend}=~/\d\d\d\d-\d\d-\d\d/){
				$datelastsend=$PAR{datelastsend};
			}
			my ($days,$messlastsend);
			if($PAR{sequence}==-1){
				#sequense disabled
				$days=-1;
				$messlastsend=0;				
			}elsif($PAR{sequence}==0){
				#sequense started
				$days=0;
				$messlastsend=0;				
			}else{
				$messlastsend=$PAR{sequence};
				map{$days=$_->{days} if ($_->{pk_mess}==$PAR{sequence})}LoadAccountSequence($PAR{account});
			}
			unless($PAR{reckey}){
				#$last=GetLastInsert("${PREF}user");
				#$db->do("INSERT INTO ${PREF}user (fk_account,name,email,days,datereg) VALUES (?,?,?,?,$NOW)",undef,$PAR{account},$PAR{name},$PAR{email},$days);
				my $params={
					messageformat=>$PAR{messageformat},
					fk_account=>$PAR{account},
					name=>$PAR{name},
					email=>$PAR{email},
					days=>$days,
					datelastsend=>$datelastsend,
					messlastsend=>$messlastsend,
					fk_affiliate=>$PAR{fk_affiliate},
					fromname=>$PAR{fromname},
					fromemail=>$PAR{fromemail},
					datereg=>$PAR{datereg}
				};
				$last=insert_db("${PREF}user",$params,{datereg=>"$NOW"});
				&Error;
			}else{
				#update user
				update_db("${PREF}user",{datereg=>$PAR{datereg},fromname=>$PAR{fromname},fromemail=>$PAR{fromemail},fk_affiliate=>$PAR{fk_affiliate},datelastsend=>$datelastsend,messlastsend=>$messlastsend,messageformat=>$PAR{messageformat},fk_account=>$PAR{account},name =>$PAR{name},email=>$PAR{email},days=>$days},{pk_user=>$PAR{reckey}});
				$last=$PAR{reckey};
			}
			
			foreach(@FIELDS){
				my $param="dp".$_->{key};
				save_user_parametr($_->{key},$last,$PAR{$param});
			}
			if (length($PAR{referer}) and $PAR{referer}=~/^http:\/\/.+$SCRIPT_NAME/){
				print $q->redirect($PAR{referer});
			}else{
				print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&act2=$PAR{act2}&account=$PAR{account}");
			}
			exit(1);
		}
	}
	#set defaults
	if ($PAR{reckey}){
		$page->add_regesp('{mode}', $LNG{TXT_MODE_EDIT});
		$val=select_one_db("SELECT * from ${PREF}user WHERE pk_user=? and fk_account=?",$PAR{reckey},$PAR{account}) 
		  || die $LNG{ERROR_USER_NOT_FOUND};
		$page->set_def('email',$val->{email});
		$page->set_def('name',$val->{name});
		$page->set_def('messageformat',$val->{messageformat});
		$page->set_def('datelastsend',$val->{datelastsend});
		$page->set_def('fk_affiliate',$val->{fk_affiliate});
		$page->set_def('fromname',$val->{fromname});
		$page->set_def('fromemail',$val->{fromemail});
		$page->set_def('datereg',$val->{datereg});
		if($val->{fk_affiliate}){
			my $aff=select_one_db("SELECT * from ${PREF}user WHERE pk_user=? and fk_account=?",$val->{fk_affiliate},$PAR{account});
			$page->add_regesp('{AFFINFO}',"<BR>$LNG{CURRENT_AFFILIATE_EMAIL} $aff->{email} \n<BR>$LNG{CURRENT_AFFILIATE_NAME} $aff->{name}");
		}else{
			$page->add_regesp('{AFFINFO}',"");
		}
		if($val->{days}==-1){
			$page->set_def('sequence',-1);
		}elsif($val->{messlastsend}){
			$page->set_def('sequence',$val->{messlastsend});
		}else{
			$page->set_def('sequence',0);
		}
		foreach (@FIELDS){
			$page->set_def('dp'.$_->{key},get_user_parametr($_->{key},$PAR{reckey}));
		}
	}else{
		$page->add_regesp("{CHECKED_yes_seq}",' CHECKED ');
		$page->set_def('days',0);
		$page->add_regesp('{mode}', $LNG{TXT_MODE_NEW});
	}
	my $add;
	foreach (@FIELDS){
		$add.=<<ALL__;
		<TR class="data">
		<td align="right"><b>$_->{name}:</b></td>
		<TD>{fm_$_->{type}_dp$_->{key}}</TD></TR>
ALL__
	}
	#return join("<BR>",map{"<B>$_</B> = $ENV{$_}"}sort keys %ENV);
	$page->set_def("referer", $ENV{HTTP_REFERER});
	add_menu_prospects($page);
	$page->add_element("sequence",0,$LNG{SEQUENCE_STATUS_STARTED});
	my @seq=LoadAccountSequence($PAR{account});
	my $i=0;
	map{
		$i++;
		$page->add_element("sequence",$_->{pk_mess},"$LNG{USR_SENT_MESSAGE} ".$i." of ".scalar(@seq)." ($LNG{SEQUENCE_DAY_SMALL} $_->{days}) $LNG{SEQUENCE_WAS_SENT}") unless ($i eq scalar(@seq));
		$page->add_element("sequence",$_->{pk_mess},uc($LNG{USR_BROWSER_FINISHED}) ." $LNG{USR_SENT_MESSAGE} ".$i." of ".scalar(@seq)." ($LNG{SEQUENCE_DAY_SMALL} $_->{days}) $LNG{SEQUENCE_WAS_SENT}") if ($i eq scalar(@seq));
	}@seq;
	$page->add_element("sequence",-1,$LNG{SEQUENCE_STATUS_DISABLED});
	$page->add_element('messageformat','0',$LNG{USR_BROWSER_DEFAULT_FORMAT});
	$page->add_element('messageformat','1',$LNG{USR_BROWSER_TEXT_USER_FORMAT});
	$page->add_element('messageformat','2',$LNG{USR_BROWSER_HTML_USER_FORMAT});
	$page->add_regesp("{LOGMESS}",&GetUserMessLog($PAR{reckey}));
	$page->ChangeData('{additional_fields}',$add);
	$page->set_default_input("text","size",35);
	$page->set_default_input("textarea","rows",4);
	$page->set_default_input("textarea","columns",35);
	$page->set_input("days",{size=>3,maxlength=>3});
	$page->ParseData;
	return $page->as_string;
}
#############
sub GetUserMessLog{
	my $user=shift;
	return unless ($user);
	my $data="";
	#return unless $CONF{messlogging};	
	my $sql="SELECT * FROM ${PREF}senthistory WHERE fk_user=? ORDER BY date ASC";
	my $out=$db->prepare($sql);
	$out->execute($user);
	&Error($sql);
	return unless ($out->rows());
	my $rows=$out->rows;
	$data.=<<ALL__;
	<h2>$LNG{USR_SENT_MESS}: $rows $LNG{USR_SENT_RECORDS_IN_LOGS}</h2>
<table width="70%" border="0" cellspacing="3" cellpadding="4" align="center">
      <tr class="dataheader"> 
        <td width="5%">&nbsp;&nbsp;</td>
	<td width="70%"> $LNG{USR_SENT_MESSAGE} </td>
	<td width="25%"> $LNG{USR_SENT_DATE} </td>
      </tr>
ALL__
	my $i;
	while (my %output=%{$out->fetchrow_hashref}){
		$i++;
		my $mess=select_one_db("SELECT * FROM ${PREF}mess WHERE pk_mess=?",$output{fk_mess});
		my $subj=sequre($mess->{subject});
		$data.=<<ALL__;
      <tr class="data"> 
        <td width="5%">$i</td>
	<td width="70%">$subj</td>
	<td width="25%"><NOBR>$output{date}</NOBR></td>
      </tr>
ALL__
	
	}
	$data.=<<ALL__;
	</TABLE>
ALL__
	
	return $data;
}
sub print_select_fields{
	if($PAR{issubmit}){
		my @params=$q->param('selectedlist');
		my $level_changed="";
		$level_changed="mode=selectfields&" if($CONF{affiliate_level} ne $PAR{affiliate_level});
		save_config($PAR{account},"REPORT_SHOW_FIELDS",join("\t",@params));
		save_config($PAR{account},"affiliate_level","$PAR{affiliate_level}");
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&${level_changed}account=$PAR{account}&act=$PAR{act}&act2=$PAR{act2}");
		exit;
	}
	my $page=new hfparser (
		DATA=>$main_shabl,
		FROM=>'#begin#reportselectfields',TO=>'#end#reportselectfields',
		ERROR_AFTER_INPUT=>0,
	);
	my $info=GetAllAccountFields($PAR{account},$CONF{affiliate_level}||0,$CONF{REPORT_SHOW_FIELDS});
	my $avalible_fields="\n";
	my $selected_fields="\n";
	map{
		my $descr=$info->{names}->{$_};
		$avalible_fields.=qq|\t<OPTION value="$_">$descr</OPTION>\n|;
	}@{$info->{avalible_fields}};
	$page->add_regesp('{avalible_list_options}',$avalible_fields);
	map{$page->add_element('affiliate_level',$_)}(0..10);
	$page->set_def('affiliate_level',$CONF{affiliate_level});
	map{
		my $descr=$info->{names}->{$_};
		$selected_fields.=qq|\t<OPTION value="$_">$descr</OPTION>\n|;
	}@{$info->{selected_fields}};
	$page->add_regesp('{selected_list_options}',$selected_fields);
	$page->ParseData;
	return $page->as_string;	

}
sub GetOrderLink{
	my $field=shift;
	
	my $direction=$PAR{direction};
	if($PAR{orderfield} eq $field){
		if($PAR{direction} eq 'asc'){
			$direction="desc"			
		}else{
			$direction="asc"
		}
	}else{
		$direction="asc"
	}
	$q->param('direction',$direction);	
	$q->param('orderfield',$field);
	my $url=$q->url(-absolute=>1,-query=>1);
	if($PAR{direction}){
		$q->param('direction',$PAR{direction});
	}else{
		$q->delete('direction');
	}
	if($PAR{orderfield}){
		$q->param('orderfield',$PAR{orderfield});
	}else{
		$q->delete('orderfield');
	}
	return $url;
	
}
sub print_users_report{
	if($PAR{mode} eq 'selectfields'){
		return print_select_fields();
	}
	if($PAR{bnAction}){
		my @USERS=$q->param('sel');
		if(@USERS){
			my $IN="(". join(',',map{$db->quote($_)}@USERS).")";

			if($PAR{action} eq 'remove'){
				map{DeleteUser($_)}@USERS;
			}elsif($PAR{action} eq 'activate'){
				$db->do("UPDATE ${PREF}user set isact =1 WHERE pk_user IN$IN");
			}elsif($PAR{action} eq 'deactivate'){
				$db->do("UPDATE ${PREF}user set isact =0 WHERE pk_user IN$IN");				
			}elsif($PAR{action} eq 'restart_sequence'){
				$db->do("UPDATE ${PREF}user set days =0, datelastsend=NULL, messlastsend=NULL  WHERE pk_user IN$IN");				
			}elsif($PAR{action} eq 'deactivate_sequence'){
				$db->do("UPDATE ${PREF}user set days =-1, datelastsend=NULL, messlastsend=NULL  WHERE pk_user IN$IN");				
			}

		}
		print $q->redirect($ENV{HTTP_REFERER}) if($ENV{HTTP_REFERER}=~/account=/);
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&act2=$PAR{act2}&act3=$PAR{act3}&account=$PAR{account}") unless ($ENV{HTTP_REFERER}=~/account=/);
		exit;
	}
	if($PAR{actsingle}){
		$db->do("UPDATE ${PREF}user SET isact=1 WHERE pk_user=?",undef,$PAR{actsingle});
		$q->delete('actsingle');
		print $q->redirect($q->url(-absolute=>1,-query=>1));
		exit;
	}
	if($PAR{inactsingle}){
		$db->do("UPDATE ${PREF}user SET isact=0 WHERE pk_user=?",undef,$PAR{inactsingle});
		$q->delete('inactsingle');
		print $q->redirect($q->url(-absolute=>1,-query=>1));
		exit;
	}
	if($PAR{removesingle}){
		DeleteUser($PAR{removesingle});
		$q->delete('removesingle');
		print $q->redirect($q->url(-absolute=>1,-query=>1));
		exit;
	}
	my @where;
	if($PAR{usedate}){
		if(length($PAR{datefrom})){
			push(@where,[datereg,">=",$PAR{datefrom}])
		}
		if(length($PAR{dateto})){
			push(@where,['datereg',"<=",$PAR{dateto}])
		}
	}
	#remove activate deactivate restart_sequence deactivate_sequence 
	#'=','>','<','>=', '<=','like','not like', 'is null','not null'
	if ($PAR{searchrule} eq 'is null' or $PAR{searchrule} eq 'is not null'){
		push(@where,[$PAR{searchbyfield},$PAR{searchrule},''])		
	}else{
		if(length($PAR{search})){
			push(@where,[$PAR{searchbyfield},$PAR{searchrule},$PAR{search}])
		}
	}
	my $all_records_count;
	my $order={};
	if(length($PAR{orderfield})){
		if($PAR{direction} eq 'desc'){
			$order->{$PAR{orderfield}}="DESC";			
		}else{
			$order->{$PAR{orderfield}}="ASC";			
		}

	}
	if($PAR{filter} eq 'act'){
		push(@where,['isact','=',1])
	}elsif($PAR{filter} eq 'dis'){
		push(@where,['isact','=',0])	
	}elsif($PAR{filter} eq 'pend'){
		push(@where,['status','<>',"$LNG{USR_BROWSER_PENDING}"]);
	}elsif($PAR{filter} eq 'ec'){	
		my @seq=LoadAccountSequence($PAR{account});
		push(@where,['sequence_now','=',scalar(@seq)]);
	}
	unless(@where){
		#if were rules empy we can query only users table
		$all_records_count=GetSQLCount("SELECT * FROM ${PREF}user WHERE fk_account=?",$PAR{account});	
	}else{
		$all_records_count=GetSQLCount(AccountUsersSQL($PAR{account},\@where,{},$CONF{affiliate_level}||0,1));
	}
	my $page=new repparser (
		DATA=>$main_shabl,
		FROM=>'#begin#reportusers',TO=>'#end#reportusers',
		ERROR_AFTER_INPUT=>0,
		ALL_ROWS_COUNT=>$all_records_count
	);
	$page->add_element("filter","",$LNG{USR_BROWSER_ALL});
	$page->add_element("filter","act",$LNG{USR_BROWSER_ACTIVE});
	$page->add_element("filter","dis",$LNG{USR_BROWSER_INACTIVE});	
	$page->add_element("filter","pend",$LNG{USR_BROWSER_PENDING});
	$page->add_element("filter","ec",$LNG{USR_BROWSER_FINISHED});		

	my $fields=GetAllAccountFields($PAR{account},$CONF{affiliate_level}||0,$CONF{REPORT_SHOW_FIELDS});
	my $names=$fields->{names};
	my @selected_fields=@{$fields->{selected_fields}};
	my @all_fields=@{$fields->{allfields}};
	my @not_selected_fields=@{$fields->{avalible_fields}};
	$page->add_element('searchbyfield','email',$LNG{FLD_EMAIL});
	$page->add_element('searchbyfield','name',$LNG{FLD_NAME});
	map{$page->add_element('searchbyfield',$_,$fields->{names}->{$_})}@selected_fields;
	map{$page->add_element('searchbyfield',$_,$fields->{names}->{$_})}@not_selected_fields;
	my @ruless=GetSQLWhereRulesArray();
	map{$page->add_element('searchrule', $_, uc($_))}@ruless;
	$page->set_def('searchrule','like');
	$page->add_regesp('{selected_fields_count}', scalar(@selected_fields));
	$page->add_regesp('{all_fields_count}', scalar(@all_fields));
	my $ADDITIONAL_FIELDS_ROWS;
	my $ADDITIONAL_FIELDS_HEADERS;
	my @text_columns=();
	if($PAR{export_to_txt}){
		push(@text_columns,$LNG{FLD_EMAIL});
		push(@text_columns,$LNG{FLD_NAME});
	}
	map{
		my $columnname=$names->{$_};
		if(/affiliate/){
			$columnname=~s/(\d+)/<sup>$1<\/sup>/;			
		}
		my $width=int(80/scalar(@selected_fields));
		if($PAR{export_to_txt}){
			push(@text_columns,"$columnname");
		}
		$ADDITIONAL_FIELDS_HEADERS.=qq|<td width="$width%" align="center"><A href="[ORDER_LINK_$_]" title="$LNG{ORDER_BY}">$columnname</A></td>\n|;
		$ADDITIONAL_FIELDS_ROWS.=qq|<td width="$width%" align="center"><NOBR>{r_$_}</NOBR></td>\n|;
		
	}@selected_fields;
	my $text_file=join("\t",@text_columns)."\r\n";
	$page->{ALL_DATA}=~s/{ADDITIONAL_FIELDS_ROWS}/$ADDITIONAL_FIELDS_ROWS/gs;
	$page->{ALL_DATA}=~s/{ADDITIONAL_FIELDS_HEADERS}/$ADDITIONAL_FIELDS_HEADERS/gs;
	$page->{ALL_DATA}=~s/\[ORDER_LINK_(.*?)\]/GetOrderLink($1)/gse;

	
	
	map{$page->add_regesp('{'.$_.'}',$PAR{$_})}keys%PAR;
	$page->add_regesp('{act3}',$PAR{act3});
	my $sql=AccountUsersSQL($PAR{account},\@where,$order,$CONF{affiliate_level}||0,0);
	unless ($PAR{export_to_txt}){
		$sql.="\n ".$page->GetLimitString;
	}
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	my @rows=();
	my %dates=shift;
	while (my $output=$out->fetchrow_hashref){
		if($PAR{export_to_txt}){
			@text_columns=();
			push(@text_columns,$output->{email});
			push(@text_columns,$output->{name});
			map{
				push(@text_columns,$output->{$_});
			}@selected_fields;
			push(@text_columns,"$columnname");
			$text_file.=join("\t",@text_columns)."\r\n";
		}else{
			$q->param(removesingle=>$output->{pk_user});
			$output->{removelink}=$q->url(-absolute=>1,-query=>1);
			$q->delete('removesingle');
			if($output->{status} eq $LNG{USR_BROWSER_INACTIVE}){
				$q->param('actsingle',$output->{pk_user});
				$output->{change_status_link}=$q->url(-absolute=>1,-query=>1);
				$output->{activation_action}=$LNG{ACTION_VALUE_ACTIVATE};
				$output->{status_image}="content.cgi?get=image&mode=gif&f=inact";
				$output->{status_link_descr}="$output->{status} $LNG{CLICK_TO} $output->{activation_action}" ;
			}elsif($output->{status} eq $LNG{USR_BROWSER_ACTIVE}){
				$q->param('inactsingle',$output->{pk_user});
				$output->{change_status_link}=$q->url(-absolute=>1,-query=>1);
				$output->{activation_action}=$LNG{ACTION_VALUE_DEACTIVATE};
				$output->{status_image}="content.cgi?get=image&mode=gif&f=active";
				$output->{status_link_descr}="$output->{status} $LNG{CLICK_TO} $output->{activation_action}" ;
			}else{#pending
				$q->param('actsingle',$output->{pk_user});
				$output->{change_status_link}=$q->url(-absolute=>1,-query=>1);
				$output->{activation_action}=$LNG{ACTION_VALUE_ACTIVATE};
				$output->{status_image}="content.cgi?get=image&mode=gif&f=pending";
				$output->{status_link_descr}="$output->{status} $LNG{CLICK_TO} $output->{activation_action}" ;				
			}
			$q->delete('inactsingle');
			$q->delete('actsingle');			
			$q->param('act3','userform');
			$q->param('reckey',$output->{pk_user});
			$output->{editlink}=$q->url(-absolute=>1,-query=>1);
			$q->delete('act3');
			$q->delete('reckey');
			map{$output->{$_}=sequre($output->{$_}) if /name|email|field/i}keys %$output;			
			$page->AddRow($output);
		}
		
	}
	$page->add_element('action',"","<>");
	map{$page->add_element('action',$_,$LNG{'ACTION_VALUE_'.uc($_)})}qw(remove activate deactivate restart_sequence deactivate_sequence );
	if($PAR{export_to_txt}){
		my $account_name=lc($ACCOUNT{$PAR{account}});
		$account_name=~s/[^a-z0-9_-]//g;
		my  $filename;
		$filename="$account_name.txt" if length($account_name);
		$filename="prospects$PAR{account}.txt" unless length($account_name);
		print "Content-type: application/octet-stream\nContent-Disposition: attachment; filename=$filename\n\n";
		print $text_file;
		exit;			
	}else{
		$page->ParseData;
		return $page->as_string; #."<HR>$sql";
	}

}
sub print_users_new{
	my %map=(
		""       =>\&print_users_report,
		'bulk' =>\&print_users_bulk,
		'import' =>\&print_users_import,
		'export' =>\&print_users_export,
		'copy'=>\&print_users_loadfrom,
		userform =>\&print_user_form,
	);
	if (exists($map{$PAR{act3}})){
		return &{$map{$PAR{act3}}};
	}else{
		$func_ref=sub{return $q->h1($LNG{ERROR_NOT_CHANGE_URL})};
		return &{$func_ref};
	}
}
###############

#################
#FIELDS
#################
sub sort_fields{
	my $account=shift;
	$sql="SELECT * from ${PREF}fields WHERE fk_account=? ORDER by rang ASC";
	my $out=$db->prepare($sql);
	&Error;
	$out->execute($PAR{account});
	&Error;
	my $i;
	while (my %output=%{$out->fetchrow_hashref}){
		$i++;
		update_db("${PREF}fields",{rang=>$i},{pk_fields=>$output{pk_fields}});
		&Error;
	}
}
################
sub delete_field{
	$db->do("DELETE FROM ${PREF}fields WHERE fk_account=? AND pk_fields=?",undef,$PAR{account},$PAR{reckey});
	$db->do("DELETE FROM  ${PREF}doppar WHERE fk_fields=",undef,$PAR{reckey});
	sort_fields($PAR{account});
	print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=columns&account=$PAR{account}&act3=fields");
	exit(1);
}
####################
sub print_field_form{
	my $ischecked_isreq;
	my %error;
	my %INPUT;	
	my $page = new hfparser(
		DATA=>$main_shabl,
		ERROR_AFTER_INPUT=>1,
		FROM=>"#begin#column_form",
		TO=>"#end#column_form",
		
	);
	
	if ($PAR{issubmit}){
		$page->set_error("fieldname",$LNG{ERROR_FIELD_NAME_INCORRECT}) if $PAR{fieldname}=~/[^a-zA-Z 0-9_\-.:]/;
		$page->set_error("fieldname","$LNG{HTML_FORM_FIELD_NAME} $PAR{fieldname} $LNG{HTML_FORM_ERR_USED}")
		  if GetSQLCount("SELECT * from ${PREF}fields where fk_account=? AND fieldname=? AND pk_fields<>?",$PAR{account},$PAR{fieldname},$PAR{reckey});
		$page->set_error("fieldname","$LNG{HTML_FORM_FIELD_NAME} $PAR{fieldname} $LNG{HTML_FORM_ERR_RESERVED}") 
		     if ($PAR{fieldname}=~/^name *$/i) or ($PAR{fieldname}=~/^email *$/i);
		$page->set_error("fieldname","$LNG{HTML_FORM_FIELD_NAME} $LNG{HTML_FORM_ERR_EMPTY}") unless $PAR{fieldname};
	}
	if ($PAR{issubmit} && !$page->is_error){
		unless($PAR{reckey}){
			##Add new
			my $isreq;
			$rang1=GetSQLCount("SELECT * from ${PREF}fields where fk_account=?",$PAR{account});
			sort_fields($PAR{account});
			insert_db("${PREF}fields",{type=>$PAR{type},fieldname=>$PAR{fieldname},fk_account=>$PAR{account},is_req=>$PAR{isreq}, rang=>$rang1+1});	
			print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=columns&account=$PAR{account}&act3=fields");
			
			exit(1);
		}else{	
			sort_fields($PAR{account});
			update_db("${PREF}fields",{fieldname=>$PAR{fieldname},fk_account=>$PAR{account},is_req=>$PAR{isreq},type=>$PAR{type}},{pk_fields=>$PAR{reckey}});	
			print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=columns&account=$PAR{account}&act3=fields");
			exit(1);
		}
	}
	####
	#set defaults
	####
	if ($PAR{reckey}){
		$val=select_one_db("SELECT * from ${PREF}fields WHERE pk_fields=?",$PAR{reckey}) || die "Atantion: bed request field  $PAR{reckey} not found";
		$page->set_def('fieldname',$val->{fieldname});
		$page->set_def('type',$val->{type});
		$page->set_def('isreq',$val->{is_req});		
	}
	$page->add_element("type","text","TEXT");
	$page->add_element("type","textarea","TEXTAREA");	
	$page->set_input('isreq',{-value=>'1' -checked=>$ischecked_isreq});
	$page->add_regesp('{body}',&print_columns_browser);
	$page->ParseData;
	return $page->as_string;
}
####################
sub print_columns_browser{
my $ret;
my $defsize=25;
my $rowssize=5;
my $max=80;
my $def_class="INPUTmy";
my $def_over_class="INPUTmyACT";

my @deftextfield=(-size=>$defsize,-maxlength=>$max,-class=>$def_class,
			-onFocus=>"this.className ='$def_over_class' ; return true;",
 			-onBlur=>" this.className ='$def_class'");			    
my @deftextarea=(-rows=>$rowssize,-columns=>$defsize,-class=>$def_class,
			-onFocus=>"this.className ='$def_over_class' ; return true;",
 			-onBlur=>" this.className ='$def_class'");			    
#"<B>".$q->a({-href=>get_full_url({act2=>fieldform,reckey=>""})},$LNG{HTML_FORM_ADD_NEW})."</B>";		
my $subm=sequre($LNG{HTML_FORM_ADD_NEW});
my $add_new_link=<<ALL__;
		<form action="$SCRIPT_NAME" method="get">
		<input type="hidden" name="ses" value="$PAR{ses}">
		<input type="hidden" name="act" value="$PAR{act}">
		<input type="hidden" name="act2" value="fieldform">
		<input type="hidden" name="act3" value="fields">		
		<input type="hidden" name="account" value="$PAR{account}">
		<div align="center"><BR><BR>
			<input type="submit" name="but" class="BUTTONmy" name="submit42" value="$subm">
		</div>		
		</form>
ALL__
	my $sql="select * from ${PREF}fields where fk_account=? order by rang";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	&Error;
	my $namefield=$q->textfield(
			-name=>'name',
                        -default=>'Jon Doe',@deftextfield
   		    );
	my $emailfield=$q->textfield(
			-name=>'email',
                        -default=>'email@host.com', @deftextfield
		    );		    
	$ret.=<<ALL__;
	<BR>
	<H2>$LNG{HTML_FORM_FIELDS}</H2><BR>
	<TABLE width="95%" border="0" cellspacing="0" cellpadding="0" align="center"> 
	<TR><TD class="line">
	<TABLE width="100%" border="0" cellspacing="1" cellpadding="3" align="center"> 
<TR class="data">
	<TD align="right"><B>$LNG{HTML_FORM_NAME}:</B></TD>
	<TD>$namefield <FONT color="red">*</FONT></TD>
	<TD colspan="3" align="center">$LNG{HTML_FORM_RESERVED}</TD>
</TR>
<TR class="data">
	<TD align="right"><B>$LNG{HTML_FORM_EMAIL}:</B></TD>
	<TD>$emailfield <FONT color="red">*</FONT></TD>
	<TD colspan="3" align="center">$LNG{HTML_FORM_RESERVED}</TD>
</TR>
ALL__
	unless ($out->rows){
		$ret.="</TD></TR></TABLE></TABLE><B>$add_new_link</B>";
		return $ret;
	}
	my $rows=$out->rows;
	$ret.=<<ALL__;
<TR class="data">
	<TD colspan="5" align="center">$LNG{HTML_FORM_YOU_HAVE} <B>$rows</B> $LNG{HTML_FORM_COSTUM_FIELDS}</TD>
</TR>
ALL__
	while (my %output=%{$out->fetchrow_hashref}){
		my $field;
		$field=$q->textfield(-name=>"df$output{pk_fields}", @deftextfield) if ($output{type} eq 'text');
		$field=$q->textarea(-name=>"df$output{pk_fields}", @deftextarea) if ($output{type} eq 'textarea');		
		my $editlink=$q->a({-title=>$LNG{PROP_IMG_DESCR},-href=>get_full_url({act2=>'fieldform',reckey=>$output{pk_fields}})},qq|<img src="content.cgi?get=image&mode=png&f=b_props" width="16" height="16" border="0">|);
		my $onCL=<<ALL__;
return confirm('$LNG{HTML_FORM_CONFIRM}');		
ALL__
		my $droplink=$q->a({-onClick=>$onCL,
				-title=>$LNG{HTML_FORM_DROP},
				-href=>get_full_url({act2=>'delfield',reckey=>$output{pk_fields}})},qq|<img src="content.cgi?get=image&mode=png&f=b_drop" width="16" height="16" border="0" alt="$LNG{HTML_FORM_DROP}">|);
		my $uplink=  $q->a({-title=> $LNG{HTML_FORM_UP},-href=>get_full_url({act2=>'up',reckey=>$output{pk_fields}})},qq|<img src="content.cgi?get=image&mode=gif&f=move_task_up" width="16" height="16" border="0" alt="$LNG{HTML_FORM_UP}">|) if $output{rang}>1;#$LNG{HTML_FORM_UP}
		$uplink=qq|<img src="content.cgi?get=image&mode=gif&f=sp" width="16" height="16" border="0">| unless $output{rang}>1;		
		my $downlink=$q->a({-title=> $LNG{HTML_FORM_DOWN},-href=>get_full_url({act2=>'down',reckey=>$output{pk_fields}})}, qq|<img src="content.cgi?get=image&mode=gif&f=move_task_down" width="16" height="16" border="0" alt="$LNG{HTML_FORM_DOWN}">| ) if $output{rang} < $out->rows;#$LNG{HTML_FORM_DOWN}
		$downlink=qq|<img src="content.cgi?get=image&mode=gif&f=sp" width="16" height="16" border="0">| unless $output{rang} < $out->rows;
		my $isreq="<FONT color=\"red\">*</FONT>" if $output{is_req};
		$ret.=<<ALL__;
<TR class="data">
	<TD align="right"><B>$output{fieldname}:<B></TD>
	<TD align="left">$field $isreq</TD>
	<TD align="center">$editlink</TD>
	<TD align="center">$droplink</TD>
	<TD align="center">$uplink $downlink</TD>	
</TR>
ALL__
	}
	$ret.=<<ALL__;
	</TR></TABLE></TD></TR></TABLE>
$add_new_link
ALL__
return $ret;
}
###################
sub get_html_code{
	my $account=shift;
	my $html;
	$account=$PAR{account} unless $account;
	my $address=$ENV{HTTP_HOST};
	my $scriptdir=$ENV{SCRIPT_NAME};
	(my $src=$scriptdir)=~s#[^/]*$##;
	my $affiliate_info_field;
	my $affiliate_info_script;
	my $validation_script;
	my $validation_code;
	my $name_online_validation;
	my $email_online_validation;
	my $addhiddenfrom;
	if($CONF{addhiddenfrom}){
		$addhiddenfrom=<<ALL__
<input type="hidden" name="fromemail" value="">
<input type="hidden" name="fromname" value="">
ALL__
	}
	
	if($CONF{add_js_validation}){
		$name_online_validation=q|ONCHANGE="validatePresent(this, 'validatenamemess');"|;
		$email_online_validation=q|ONCHANGE="validateEmail(this, 'validateemailmess', true);"|;
		$validation_code=q|onSubmit="return validateOnSubmit()"|;
		my $p2=new dparser(
			DATA=>"$SHABL_DIR/formval.js",
			IS_CRIPT=>0	
		);
		$p2->ParseData();
		my $script=$p2->as_string;
		$validation_script=<<ALL__;
<!--Form validation-->
<script language="JavaScript">
$script
</script>
<!--End form validation-->
ALL__
	}
	if($CONF{collect_affiliate_info}){
		$affiliate_info_field=qq|<input type="hidden" id="affiliate_collect" name="affiliate_collect" value="">|;
		$affiliate_info_script=q|<!--Collecting affiliate informaion-->
<script language="JavaScript">
function createRequestObject() {
  FORM_DATA = new Object();
  separator = ',';
  query = '' + this.location;
  qu = query;
  query = query.substring((query.indexOf('?')) + 1);
  if (query.length < 1) { return false; }  
  keypairs = new Object();
  numKP = 1;
  while (query.indexOf('&') > -1) {
    keypairs[numKP] = query.substring(0,query.indexOf('&'));
    query = query.substring((query.indexOf('&')) + 1);
    numKP++;
  }
  keypairs[numKP] = query;
  for (i in keypairs) {
    keyName = keypairs[i].substring(0,keypairs[i].indexOf('='));
    keyValue = keypairs[i].substring((keypairs[i].indexOf('=')) + 1);
    while (keyValue.indexOf('+') > -1) {
      keyValue = keyValue.substring(0,keyValue.indexOf('+')) + ' ' + keyValue.substring(keyValue.indexOf('+') + 1);
    }
    keyValue = unescape(keyValue);
    if (FORM_DATA[keyName]) {
      FORM_DATA[keyName] = FORM_DATA[keyName] + separator + keyValue;
    } else {
      FORM_DATA[keyName] = keyValue;
    }
  }
  return FORM_DATA;
}
var FORM_DATA = createRequestObject();
if(FORM_DATA['ref']!= null){
	var hiddenaffiliate=document.getElementById('affiliate_collect');
	hiddenaffiliate.value=FORM_DATA['ref'];
}
</script>
<!--End of collecting affiliate informaion-->|
	}
	$html=<<ALL__;
<!-- Start form -->
$validation_script
<form name="subscribeform" method="post" $validation_code action="http://$address${src}register.cgi">
  <input type="hidden" name="account" value="$account"> $affiliate_info_field 
  $addhiddenfrom
  <table width="100%" border="0" cellspacing="0" cellpadding="4">
   <tr>
    <td align="right" width="49%"><b>$LNG{HTML_FORM_NAME}:</b></td>
    <td width="10%">
     <input type="text" name="name" size="25" maxlength="40" $name_online_validation>
    </td>
    <td width="40%" id="validatenamemess" align="left" style="color : red; white-space: nowrap; font-weight : bold;">*</td>
   </tr>
   <tr> 
    <td align="right" width="49%"><b>$LNG{HTML_FORM_EMAIL}:</b></td>
    <td width="10%">
     <input type="text" name="email" size="25" maxlength="40" $email_online_validation>
    </td>
    <td width="40%" id="validateemailmess" align="left" style="color : red; white-space: nowrap; font-weight : bold;">*</td>
   </tr>
ALL__
if($CONF{allowchoiseformat}){
$html.=<<ALL__;
   <tr> 
    <td align="right" width="50%"><b>$LNG{HTML_FORM_MESSFORMAT}:</b></td>
    <td  colspan="2">
     <SELECT name="messageformat">
     <OPTION value="0">--Select--</OPTION>
     <OPTION value="1">Text</OPTION>
     <OPTION value="2">HTML</OPTION>
     </SELECT>
    </td>
   </tr>
ALL__
}
	
	$sql="SELECT * from ${PREF}fields WHERE fk_account=? ORDER by rang";
	my $out=$db->prepare($sql);
	
	&Error;
	$out->execute($account);
	&Error;
	my @additional_validation;
	while (my %output=%{$out->fetchrow_hashref}){
		my $isrec;
		my $innput;
		my $online_validation="";
		if ($output{is_req} ==1 and $CONF{add_js_validation}){
			$online_validation=qq| ONCHANGE="validatePresent(this, 'errmess$output{pk_fields}');"|;
		}
		if ($output{type} eq 'text'){
			$innput=<<ALL__;
 <input type="text" name="dp$output{pk_fields}" size="25" maxlength="40"$online_validation>
ALL__
		}else{
	$innput=<<ALL__;
 <TEXTAREA name="dp$output{pk_fields}" rows="4" columns="25"$online_validation>
 </TEXTAREA>
ALL__

		}
		$isrec="<font color=\"red\">*</font>" if ($output{is_req} ==1);
		if ($output{is_req} ==1){
			$html.=<<ALL__;
 <tr> 
  <td align="right" width="50%"><b>$output{fieldname}:</b></td>
   <td width="10%" >
     $innput 
  </td>
   <td width="40%" id="errmess$output{pk_fields}" align="left" valign="middle" style="color : red; white-space: nowrap; font-weight : bold;">
     * 
  </td>  
 </tr>
ALL__
			push(@additional_validation,qq|if (!validatePresent(document.forms.subscribeform.dp$output{pk_fields},  'errmess$output{pk_fields}'))        errs += 1;|);
		}else{
$html.=<<ALL__;
 <tr> 
  <td align="right" width="50%"><b>$output{fieldname}:</b></td>
   <td width="50%" colspan="2">
     $innput 
  </td>
 </tr>
ALL__
		}
	}
my $additional_validation=join("\n",@additional_validation);
$html=~s/{validate_additional}/$additional_validation/;
my @optional_subscribe=split(/\|/,$CONF{optional_subscribe});
if(scalar(@optional_subscribe)){
$html.=<<ALL__;	
 <!--OPTIONAL SUBSCRIBE -->
 <tr>
   <td  width="50%">&nbsp;</td>
   <td align="left" width="50%" colspan="2"> 
ALL__
my @ch=();
map{push(@ch,$q->checkbox('optional_subscribe',	'',	$_,	"$LNG{HTML_FORM_OTIONAL_SUBSCRIBE_CKECKBOX} $ACCOUNT{$_}")
	)}@optional_subscribe;
$html.=join("<BR>\n", @ch);
$html.=<<ALL__;	
   </td>
 </tr>
  <!--END OPTIONAL SUBSCRIBE -->
ALL__

}
$html.=<<ALL__;	
 <tr> 
   <td align="center" colspan="3"> <input type="submit" value="$LNG{HTML_FORM_SUBSCRIBE}"></td>
 </tr>
 </table>
</form>
$affiliate_info_script	      
<!-- End form -->
ALL__
	return $html;
}
sub print_htmlform_settings{
	my $page = new hfparser(
		DATA=>$main_shabl,
		FROM=>'#start#htmlformsettings',
		TO=>'#end#htmlformsettings'		
	);
	my @simple_fields=qw(allowchoiseformat add_js_validation unsub_unsubscribed_all collect_affiliate_info unsub_account_all suspend_account_all lock_account_all addhiddenfrom);
	if($PAR{issubmit}){
		save_config($PAR{account},"optional_subscribe",join("|",$q->param('optional_subscribe')));
		save_config($PAR{account},"ADD_ACCOUNTS",join("|",$q->param('addaccount')));
		save_config($PAR{account},"ADD_ACCOUNTS_UNSUBSCRIBE",join("|",$q->param('unsub_account')));
		save_config($PAR{account},"ADD_ACCOUNTS_SUSPEND",join("|",$q->param('suspend_account')));
		save_config($PAR{account},"ADD_ACCOUNTS_LOCK",join("|",$q->param('lock_account')));
		save_config($PAR{account},"unsubscribe_when_unsubscribed",join("|",$q->param('unsubscribe_when_unsubscribed')));
		map{save_config(0,$_,$PAR{$_})}qw(ipbanlist ipbanlist_error);
		map{save_config($PAR{account},$_,$PAR{$_})}@simple_fields;
		$page->add_regesp("{mess}","<h2 class=\"mess\">$LNG{MESS_SETTINGS_UPDATED}</h2>");
	}else{
		$page->add_regesp("{mess}","");

	}
	my @Acc=();
	map{push (@Acc,$_) if($_ != $PAR{account})}@ACCOUNT_ORDER;
#	die(join("\n",@Acc));
	my @def_optional_subscribe=split(/\|/,$CONF{optional_subscribe});
	my @def_automatic_subscribe=split(/\|/,$CONF{ADD_ACCOUNTS});
	my @def_unsubscribe_when_subscribed=split(/\|/,$CONF{ADD_ACCOUNTS_UNSUBSCRIBE});
	my @def_suspend_when_subscribed=split(/\|/,$CONF{ADD_ACCOUNTS_SUSPEND});
	my @def_lock_when_subscribed=split(/\|/,$CONF{ADD_ACCOUNTS_LOCK});
	my @def_unsubscribe_when_unsubscribed=split(/\|/,$CONF{unsubscribe_when_unsubscribed});
	$page->add_regesp('{yourIP}',$ENV{REMOTE_ADDR});	
	$page->add_regesp('{optional_subscribe}',join("",$q->checkbox_group('optional_subscribe',\@Acc,\@def_optional_subscribe,'true',\%ACCOUNT)));
	$page->add_regesp('{automatic_subscribe}',join("",$q->checkbox_group('addaccount',\@Acc,\@def_automatic_subscribe,'true',\%ACCOUNT)));
	$page->add_regesp('{unsubscribe_when_subscribed}',join("",$q->checkbox_group('unsub_account',\@Acc,\@def_unsubscribe_when_subscribed,'true',\%ACCOUNT)));
	$page->add_regesp('{suspend_when_subscribed}',join("",$q->checkbox_group('suspend_account',\@Acc,\@def_suspend_when_subscribed,'true',\%ACCOUNT)));
	$page->add_regesp('{lock_when_subscribed}',join("",$q->checkbox_group('lock_account',\@Acc,\@def_lock_when_subscribed,'true',\%ACCOUNT)));
	$page->add_regesp('{unsubscribe_when_unsubscribed}',join("",
			$q->checkbox_group('unsubscribe_when_unsubscribed',\@Acc,\@def_unsubscribe_when_unsubscribed,'true',\%ACCOUNT)));
	map{$page->set_def($_,$CONF{$_})}@simple_fields;
	map{$page->set_def($_,$CONF{$_})}qw(ipbanlist ipbanlist_error);
	$page->set_def('ipbanlist_error',$LNG{IP_BAN_ERROR_MESSAGE_DEFAULT}) unless(length($CONF{ipbanlist_error}));
	
	$page->ParseData;
	return $page->as_string;
}
sub print_integration{
	my $page = new hfparser(
		DATA=>$main_shabl,
		FROM=>'#begin#htmlform#integration',
		TO=>'#end#htmlform#integration'		
	);
	my $sql=AccountUsersSQL($PAR{account},[],{pk_user=>'asc'},$CONF{affiliate_level}||0,0);
	$page->add_regesp("{sql}",$sql);
	my $perl_fields="\n";
	my @FIELDS=load_account_fields($PAR{account});
	my @QUERY=('account => '.$PAR{account},'name=>$name','email => $email');
	my @ex=('\'useremail@hotmail.com\'','\'John Doe\'');
	my @phpfields=qw($email $name);
	my @jsfields=qw(email name);
	my @phpquery=('account=$account','email=$email', 'name=$name');
	my @js_add_fields_encode=();
	map{
		$perl_fields.="\tmy \$field$_->{key}=shift; #Custom filed $_->{name}\n";
		push(@phpfields,'$field'.$_->{key});
		push(@jsfields,'field'.$_->{key});
		push(@phpdescr,'//$field'.$_->{key}." - Custom filed $_->{name}");
		push(@jsdescr,'//field'.$_->{key}." - Custom filed $_->{name}");
		push(@js_add_fields_encode,qq|\tpairs.push("dp$_->{key}=" + encodeURIComponent(field$_->{key}));|);
		
		push(@QUERY,"dp$_->{key} => \$field$_->{key}");
		push(@phpquery,"dp$_->{key}=\$field$_->{key}");
		push(@ex,"\'$_->{name} value\'");
	}@FIELDS;
	@QUERY=map{"\n\t\t\t$_"}@QUERY;

	my $query=join(", ",@QUERY);
	my $perl_code=q|#/usr/bin/perl
use HTTP::Request::Common qw(POST);
use LWP::UserAgent;

#RegisterProspect function will send all information to register.cgi 
#Here is exaple of using this fuction
#RegisterProspect(|.join(',',@ex).q|);
#
sub RegisterProspect{
	my $email=shift;
	my $name=shift;|.$perl_fields.q|

	$ua = LWP::UserAgent->new;
	$ua->agent('Mozilla/5.0');
	my $req = POST '|."$CONF{serverurl}register.cgi".q|',
		[ |.$query.q| 
		];
	$ua->request($req);
}
|;
	$perl_code=~s/\n/<BR>/gs;
	$perl_code=~s/\t/&nbsp;&nbsp;&nbsp;&nbsp;/gs;
	$page->add_regesp("{perl}",$perl_code);


	my $phpvars=join(',', @phpfields);
	my $phpencode=join("\n", map{"\t$_=urlencode($_);"}@phpfields);
	my $phpdesk=join("\n", @phpdescr);
	my $phpquery=join('&',@phpquery);
my $php_code=q|
<?
//RegisterProspect function will send all information to register.cgi 
//Here is exaple of using this fuction
//RegisterProspect(|.join(',',@ex).q|);
function RegisterProspect(|.$phpvars.q|)
{
|.$phpdesk.q|
|.$phpencode.q|
	$URL="|."$CONF{serverurl}register.cgi".q|";
	$account=|.$PAR{account}.q|;
	$ch = curl_init();   
	curl_setopt($ch, CURLOPT_URL,"$URL"); 
	curl_setopt($ch, CURLOPT_POST, 1);
	curl_setopt($ch, CURLOPT_POSTFIELDS, 
		"|.$phpquery.q|"
	);
	curl_exec ($ch);    
	curl_close ($ch);
}
?>
|;
	$php_code=sequre($php_code);
	#$php_code=~s/\n/<BR>/gs;
	$php_code=~s/\t/&nbsp;&nbsp;&nbsp;&nbsp;/gs;
	$page->add_regesp("{php}",$php_code);

	my $jsfields=join(',', @jsfields);
	my $phpencode=join("\n", map{"\t$_=encodeURIComponent($_);"}@phpfields);
	my $phpdesk=join("\n", @phpdescr);
	my $phpquery=join('&',@phpquery);
	my $js_add_fields_encode	= join("\n",@js_add_fields_encode);
my $js_code=q|
<script language="JavaScript">
//RegisterProspect function will send all information to register.cgi 
//Here is exaple of using this fuction
//<form action="register.php" onSubmit="RegisterProspect(|.join(',',@ex).q|");

function RegisterProspect(|.$jsfields.q|)
{
|.$phpdesk.q|
	var url="|."$CONF{serverurl}register.cgi".q|";
	var account=|.$PAR{account}.q|;
	var pairs = new Array();
	pairs.push("account=" + encodeURIComponent(account));
	pairs.push("email=" + encodeURIComponent(email));
	pairs.push("name=" + encodeURIComponent(email));
|.$js_add_fields_encode.q|	
	var query=pairs.join("&");
	var contentType = "application/x-www-form-urlencoded; charset=UTF-8";
	// Native XMLHttpRequest object
	if (window.XMLHttpRequest) {
		request = new XMLHttpRequest();
		request.open("post", url, true);
		request.setRequestHeader("Content-Type", contentType);
		request.send(query);
	// ActiveX XMLHttpRequest object
	} else if (window.ActiveXObject) {
		request = new ActiveXObject("Microsoft.XMLHTTP");
		if (request) {
			request.open("post", url, true);
			request.setRequestHeader("Content-Type", contentType);
			request.send(query);
		}
    	}
}
</script>
|;
	$js_code=sequre($js_code);
	#$php_code=~s/\n/<BR>/gs;
	$js_code=~s/\t/&nbsp;&nbsp;&nbsp;&nbsp;/gs;

	$page->add_regesp("{ajax}",$js_code);
	
	$page->ParseData;
	return $page->as_string;

}
###################
sub print_columns{
	return &print_columns_browser  if($PAR{act3} eq 'fields');
	return &print_htmlform_settings  if($PAR{act3} eq 'settings');
	return &print_integration  if($PAR{act3} eq 'integration');
	my $page = new hfparser(
		DATA=>$main_shabl,
		FROM=>'#begin#column_browser',
		TO=>'#end#column_browser'		
	);

	sort_fields($PAR{account});
	$page->set_input('htmlcode',{columns=>80,default=>get_html_code($PAR{account})});
	$page->add_regesp('{formPrewiew}',get_html_code($PAR{account}));
	
	#$page->add_regesp('{body}',&print_columns_browser);
	
	$page->ParseData;
	return $page->as_string;
}
#############
sub get_user_parametr{	
my $field=shift;
my $user=shift;
my $out;
my $out=select_one_db("SELECT * from ${PREF}doppar WHERE fk_fields=? AND fk_user=?",$field,$user);
return $out->{value};
}

#####################
#sub print_undeliv{
#	my @params=(qw(isbounce bnaccount replyto bnpop3server bnpop3user bnpop3pass bnpop3port bncount bnaction));
#	my @req=();
#	my $page = new hfparser(
#		DATA=>$main_shabl		
#	);
#	if ($PAR{issubmit}){
#		if($PAR{isbounce}){
#			push(@req,qw(replyto bnpop3server bnpop3user bnpop3pass bnpop3port bncount bnaction))
#		}
#		foreach (@req){
#			$page->set_error($_,$LNG{ERROR_REQUIRED}) if ($PAR{$_} eq '');
#		}
#		if (length($PAR{bnpop3port})>0){
#			if ($PAR{bnpop3port}=~/[^0-9]/){
#				$page->set_error('bnpop3port',"Must be the number");
#			}
#		}
#		if (length($PAR{bncount})>0){
#			if ($PAR{bncount}=~/[^0-9]/){
#				$page->set_error('bncount',"Must be the number");
#			}
#			if ($PAR{bncount}<1){
#				$page->set_error('bncount',"Must be more then 0");
#			}
#		}
#		unless ($page->is_error){
#			foreach(@params){
#				save_config($PAR{account},$_,$PAR{$_});
#			}
#			$page->add_regesp('{error}', qq|<h1 class="mess">$LNG{MESS_SETTINGS_UPDATED}</h1>|);
#		}
#	}
#	####
#	foreach(@params){
#		$page->set_def($_,$CONF{$_});
#	}
#	$page->set_def('bnpop3port',110) unless $CONF{bnpop3port};
#	$page->set_def('bncount',5) unless $CONF{bncount};	
#	$page->set_default_input("text","size",35);
#	#$page->set_default_input("textarea","rows",4);
#	$page->add_element('bnaction','remove','Remove from database');
#	$page->add_element('bnaction','inact',"Set $LNG{USR_BROWSER_INACTIVE}");
#	$page->add_element('bnaccount','this','in current account');
#	$page->add_element('bnaccount','all','in all accounts');	
#	$page->set_input("bnpop3port",{size=>4, MAXLENGTH=>5});
#	$page->set_input("bncount",{size=>4, MAXLENGTH=>5});
#	$page->SplitData("#begin#undeliv","#end#undeliv");
#	$page->deleteBEFORE_AFTER();	
#	$page->ParseData;
#	return $page->as_string;
#}
#####################
sub print_config_rss{
	my $page = new hfparser(
		DATA=>$main_shabl,
		FROM=>'#start#rss',TO=>'#end#rss'	
	);
	my @text_params=qw(rss_title rss_description rss_copy_line rss_ti_title rss_ti_description rss_ti_link rss_ti_name rss_link);
	my @check_params=qw(rss_use_text_input);
	my @params=(@text_params,@check_params,qw(rss_lang rss_encoding));
	map{$page->set_def($_,$CONF{$_})}@params;
	$page->add_element('rss_encoding','utf-8','utf-8 ('.$LNG{RSS_DEF_ENC}.")");
	map{$page->add_element('rss_lang',$_,$rss_languages{$_}." [$_]");}sort keys %rss_languages;
	$page->set_def('rss_lang','en')unless($CONF{rss_lang});
	map{$page->add_element('rss_encoding',$_,$ENCODINGS{$_});}sort {$ENCODINGS{$a} cmp $ENCODINGS{$b}} keys %ENCODINGS;
	my @req=qw(rss_title rss_description);
	@req=(@req,qw(rss_ti_title rss_ti_description rss_ti_link rss_ti_name))if($PAR{rss_use_text_input});
	map{$page->set_input($_,{size=>30})}@text_params;
	if($PAR{issubmit}){
		map{$page->set_error($_,$LNG{ERROR_REQUIRED}) unless length($PAR{$_})}@req;
		if(length($PAR{rss_link})){
			$page->set_error('rss_link',$LNG{ERROR_URL_INCORRECT}) unless check_url($PAR{rss_link});
		}
		if(length($PAR{rss_ti_link})){
			$page->set_error('rss_ti_link',$LNG{ERROR_URL_INCORRECT}) unless check_url($PAR{rss_ti_link});			
		}
		unless($page->is_error){
			map{save_config($PAR{account},$_,$PAR{$_})}@params;
			$page->add_regesp('{error}', qq|<h1 class="mess">$LNG{MESS_SETTINGS_UPDATED}</h1>|);	
		}
	}
	$page->ParseData;
	return $page->as_string;
	
}
sub print_config{
	return print_config_rss() if($PAR{act3} eq 'rss');
	my %httppars=(redirsub=>0, redirrem=>0,doiconfurl=>0, alreadyremoved=>0, alreadysub=>0);
	my @params=(qw(prefpagetempl alreadyremoved alreadysub adminname adminemail replyto messlogging defname subscribeemail pop3server pop3user pop3pass pop3port fromname fromemail  ispurge isnotifsubscr isnotifunsubscr isdoi doiconfurl ispop3 banmails banmailserror defcharset no_uppercase addunsubscribelinkauto personalizedsub subscribetemplate personalizeddoi doiconftemplate allow_modyfy_format disable_modify confirm_modify_body confirm_modify_subject notify_about_modification),keys %httppars);
	my @req=(qw(defname fromemail fromname redirrem));
	my $page = new hfparser(
		DATA=>$main_shabl		
	);
	if ($PAR{issubmit}){
		unless($PAR{disable_modify}){
			push(@req,qw(confirm_modify_body confirm_modify_subject));
		}
		if(length($PAR{confirm_modify_body})){
			$page->set_error("confirm_modify_body",$LNG{ERROR_TAG_CONFIRM_REQUIRED}) unless ($PAR{confirm_modify_body}=~/\[CONFIRM_URL\]/);
		}
		if($PAR{personalizedsub}){
			push(@req,'subscribetemplate')
		}else{
			$httppars{redirsub}=1;
		}
		if($PAR{isdoi}){
			if($PAR{personalizeddoi}){
				push(@req,'doiconftemplate')
			}else{
				$httppars{doiconfurl}=1 ;
			}
		}
		
		if($PAR{ispop3}){
			push(@req,qw(pop3server pop3user pop3pass pop3port subscribeemail))
		}
		if($PAR{banmails}){
			push(@req,'banmailserror')
		}
		
		if($PAR{isnotifsubscr} or $PAR{isnotifunsubscr}){ 
			push(@req,qw(adminname adminemail));
			$page->set_error("adminemail",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{adminemail},0));
		}
#		if($PAR{returnpath}){ 
#			$page->set_error("returnpath",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{returnpath},0));
#		}
#		if($PAR{errorsto}){ 
#			$page->set_error("errorsto",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{errorsto},0));
#		}		
		
		$httppars{redirrem}=1; #if $PAR{isaddunsubscrlink};
		foreach (keys %httppars){
			$page->set_error($_,$LNG{ERROR_URL_INCORRECT}) unless check_url($PAR{$_},$httppars{$_});
		}
		foreach (@req){
			$page->set_error($_,$LNG{ERROR_REQUIRED}) if ($PAR{$_} eq '');
		}
		$page->set_error("fromemail",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{fromemail},0));
		if ($PAR{pop3port}){
			if ($PAR{pop3port}=~/[^0-9]/){
				$page->set_error('pop3port',$LNG{ERROR_NUMBER_REQUIRED});
			}
		}
		unless ($page->is_error){
			foreach(@params){
				#$PAR{$_}=~s/^(http:\/\/+)+// if exists($httppars{$_});
				if($_ eq 'alreadyremoved'){
					save_config(0,$_,$PAR{$_});
				}else{
					save_config($PAR{account},$_,$PAR{$_});
				}
				
				
			}
			$page->add_regesp('{error}', qq|<h1 class="mess">$LNG{MESS_SETTINGS_UPDATED}</h1>|);
		}
	}
	foreach (@params){
		if (exists($httppars{$_})){
			$CONF{$_}="http://" unless $CONF{$_};
		}
		$page->set_def($_,$CONF{$_});
	}
	unless($CONF{confirm_modify_body}){
		my $mess_text=<<ALL__;
Hello, [FIRSTNAME].

Please click on the link below to confirm that you've changed your contact information.

[CONFIRM_URL]

---------------
If this message was sent you by mistake, please, do not click on the link above.
Powered by Follow Up Mailing List Processor Pro
http://www.sellwide.com/
ALL__
		$page->set_def('confirm_modify_body',$mess_text);
	}
	unless($CONF{confirm_modify_subject}){
		$page->set_def('confirm_modify_subject',"Please confirm...");
	}
	
	####
	$page->add_element('defcharset','',$LNG{TXT_DEFAULT});
	map{$page->add_element('defcharset',$_,$ENCODINGS{$_});}sort {$ENCODINGS{$a} cmp $ENCODINGS{$b}} keys %ENCODINGS;
	opendir(DIR,$TempatesSubscribeDir);
	my @backups;
	$page->add_element('subscribetemplate','','');
	while(my $file=readdir(DIR)){
		next unless $file=~/\.s?html?$/;
		$page->add_element('subscribetemplate',$file);
	}
	opendir(DIR,$TempatesDoiDir);
	my @backups;
	$page->add_element('doiconftemplate','','');
	while(my $file=readdir(DIR)){
		next unless $file=~/\.s?html?$/;
		$page->add_element('doiconftemplate',$file);
	}
	opendir(DIR,$TempatesPrefDir);
	my @backups;
#	$page->add_element('prefpagetempl','','');
	while(my $file=readdir(DIR)){
		next unless $file=~/\.s?html?$/;
		$page->add_element('prefpagetempl',$file);
	}	
	$page->add_regesp('{dir_sub}',$TempatesSubscribeDir);
	$page->add_regesp('{dir_doi}',$TempatesDoiDir);
	$page->add_regesp('{dir_pref}',$TempatesPrefDir);
	$page->set_default_input("text","maxlength",180);
	$page->set_default_input("text","size",35);
	$page->set_default_input("textarea","rows",4);
	$page->set_default_input("textarea","columns",35);
	$page->set_input("pop3port",{size=>4, MAXLENGTH=>5});
	$page->SplitData("#begin#config","#end#config");
	$page->deleteBEFORE_AFTER();	
	$page->ParseData;
	return $page->as_string;
}
####################
sub print_main_account_data{

	my $page = new hfparser(
		DATA=>$main_shabl		
	);
	$page->SplitData("#begin#main","#end#main");
	$page->deleteBEFORE_AFTER();
	$page->add_regesp('{main_menu_body}',get_full_menu(\@ACCOUNTMENU));
	$page->add_regesp('{account}',$PAR{account});
	$page->add_regesp('{total_prospects}',GetSQLCount("Select * from ${PREF}user WHERE fk_account=?",$PAR{account}));
	$page->add_regesp('{total_active}',GetSQLCount("Select * from ${PREF}user WHERE fk_account=? AND  isact=1",$PAR{account}));
	$page->add_regesp('{total_inactive}',GetSQLCount("Select * from ${PREF}user WHERE fk_account=? AND  isact<>1",$PAR{account}));
	$page->ParseData;
	return $page->as_string;
}
#first for account
##########################
sub move_down_field{
sort_fields($PAR{account});
my $el=select_one_db("SELECT * from ${PREF}fields WHERE pk_fields=?",$PAR{reckey});
my $rang=$el->{rang};
my $count= GetSQLCount("SELECT * from ${PREF}fields WHERE fk_account=?",$PAR{account});
if ($rang<$count){
 	$db->do("UPDATE ${PREF}fields Set rang=$rang WHERE fk_account=? and rang=$rang+1",undef, $PAR{account});
	&Error;
	$db->do("UPDATE ${PREF}fields Set rang=rang+1 WHERE pk_fields=?",undef, $PAR{reckey});
	&Error; 
}
sort_fields($PAR{account});
print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=columns&account=$PAR{account}&act3=fields");
exit();
}
#######################
sub move_up_field{
sort_fields($PAR{account});
my $el=select_one_db("SELECT * from ${PREF}fields WHERE pk_fields=?",$PAR{reckey});
my $rang=$el->{rang};
my $count= GetSQLCount("SELECT * from ${PREF}fields WHERE fk_account=?",$PAR{account});
if ($rang>1){
 	$db->do("UPDATE ${PREF}fields Set rang=$rang WHERE fk_account=? and rang=$rang-1",undef, $PAR{account});
	&Error;
	$db->do("UPDATE ${PREF}fields Set rang=rang-1 WHERE pk_fields=?",undef, $PAR{reckey});
	&Error; 
}
sort_fields($PAR{account});
print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=columns&account=$PAR{account}&act3=fields");
exit();
}
######################
sub print_users_loadfrom{
	my $page = new hfparser(
		DATA=>$main_shabl		
	);
	$page->SplitData("#start#user_loadfrom","#end#user_loadfrom");
	add_menu_prospects($page);
	$page->deleteBEFORE_AFTER;
	if($PAR{issubmit}){
		my $add;
		$add="AND isact='1'" if ($PAR{activ} eq 'act');
		$add="AND isact='0'" if ($PAR{activ} eq 'dis');
		my $sql="SELECT * FROM ${PREF}user WHERE fk_account=?  $add";
		my $out=$db->prepare($sql);
		$out->execute($PAR{'import'});
		my @OUT=();
		while (my %output=%{$out->fetchrow_hashref}){
			delete($output{pk_user});
			$output{fk_account}=$PAR{account};
			insert_db("${PREF}user",\%output) unless GetSQLCount("SELECT * FROM ${PREF}user WHERE fk_account=? AND email=?",$PAR{account},$output{email});
		}
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=users&account=$PAR{account}");
		exit;
	}
	$page->add_element("activ","",$LNG{USR_BROWSER_ALL});
	$page->add_element("activ", "act", $LNG{USR_BROWSER_ACTIVE});
	$page->add_element("activ", "dis", $LNG{USR_BROWSER_INACTIVE});
	my $sql="SELECT ${PREF}account.name as name,${PREF}account.pk_account as reckey, count(pk_user) as mycount  FROM  ${PREF}account LEFT JOIN  ${PREF}user ON fk_account=pk_account  WHERE pk_account <> ? GROUP BY fk_account HAVING mycount>0";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	&Error($sql);
	unless($out->rows){
		$page->SplitData("<!--START_RESULT-->","<!--END_RESULT-->");
		$page->replaceINSIDE("<h1 class=\"mess\">$LNG{USR_BROWSER_CANT_IMPORT}</H1>");
		
	}
	while (my %output=%{$out->fetchrow_hashref}){
		$page->add_element("import",$output{reckey},"$output{name} [$output{mycount}]");
	}
		
	
	$page->ParseData;
	return $page->as_string;	
}
sub print_users_tab_export{
	my $allcount=GetSQLCount("SELECT * FROM ${PREF}user WHERE fk_account=? ",$PAR{account});
	my $page = new hfparser(
		DATA=>$main_shabl,FROM=>"#start#user_tabexport",TO=>"#end#user_tabexport"
	);
	my @where;
	if($PAR{filter} eq 'act'){
		push(@where,['isact','=',1])
	}elsif($PAR{filter} eq 'dis'){
		push(@where,['isact','=',0])	
	}elsif($PAR{filter} eq 'pend'){
		push(@where,['status','<>',"$LNG{USR_BROWSER_PENDING}"]);
	}elsif($PAR{filter} eq 'ec'){	
		my @seq=LoadAccountSequence($PAR{account});
		push(@where,['sequence_now','=',scalar(@seq)]);
	}
	$page->add_element("filter","",$LNG{USR_BROWSER_ALL});
	$page->add_element("filter","act",$LNG{USR_BROWSER_ACTIVE});
	$page->add_element("filter","dis",$LNG{USR_BROWSER_INACTIVE});
	$page->add_element("filter","pend",$LNG{USR_BROWSER_PENDING});
	$page->add_element("filter","ec",$LNG{USR_BROWSER_FINISHED});
	if($PAR{issubmit}){
		my $sql=AccountUsersSQL($PAR{account},\@where,{email=>"ASC"},0,0);
		my $accountfields=GetAllAccountFields($PAR{account},0,{});
		my @import_fields=qw(email name datereg ip);
		my $names=$accountfields->{names};
		$names->{email}=$LNG{FLD_EMAIL};
		$names->{name}=$LNG{FLD_NAME};
		my @add_fields=();
		map{ if (/^field\d+/){push(@import_fields,$_);push(@add_fields,$_)}}@{$accountfields->{allfields}};
		map{$page->add_regesp("{$_}",$PAR{$_})}keys %PAR;
		print "Content-type: application/octet-stream\nContent-Disposition: attachment; filename=sample.txt\n\n";
		print join("\t",map{$names->{$_}}@import_fields)."\r\n";
		my $out=$db->prepare($sql);
		$out->execute();
		&Error($sql);
		my @rows=();
		my %dates=shift;
		while (my $output=$out->fetchrow_hashref){
			print join("\t",
				map{
					$output->{$_}=~s/\t|\r|\n/ /g;
					$output->{$_};
				}@import_fields)."\r\n";
		}	
		exit;
				
#			print "Content-type: application/octet-stream\nContent-Disposition: attachment; filename=prospects.txt\n\n";
#			print join("\n",@OUT);
#			exit;
	}
	unless($allcount){
		$page->SplitData("<!--START_RESULT-->","<!--END_RESULT-->");
		$page->replaceINSIDE($q->h1($LNG{USR_BROWSER_CANT_EXPORT}));
	}	
	$page->add_regesp('{all_count}',$allcount);
	$page->add_regesp('{account}',$PAR{account});
	$page->ParseData;
	return $page->as_string;
}
######################
sub print_users_export{
	return &print_users_tab_export if($PAR{act4} eq 'tab');
	my $allcount=GetSQLCount("SELECT * FROM ${PREF}user WHERE fk_account=? ",$PAR{account});
	my $page = new hfparser(
		DATA=>$main_shabl,FROM=>"#start#user_export",TO=>"#end#user_export"
	);
	if($PAR{issubmit}){
		my $add;
		$add="AND isact='1'" if ($PAR{activ} eq 'act');
		$add="AND isact='0'" if ($PAR{activ} eq 'dis');
		my $sql="SELECT * FROM ${PREF}user WHERE fk_account=?  $add";
		my $out=$db->prepare($sql);
		&Error;
		$out->execute($PAR{account});
		&Error;
		my @OUT=();
		while (my %output=%{$out->fetchrow_hashref}){
			my $shabl=$PAR{format};
			$shabl=~s/TAB/\t/;
			$shabl=~s/--email--/$output{email}/;
			$shabl=~s/--name--/$output{name}/;
			push(@OUT,$shabl);
		}
		if ($PAR{to} eq 'file'){
			print "Content-type: application/octet-stream\nContent-Disposition: attachment; filename=prospects.txt\n\n";
			print join("\n",@OUT);
			exit;
		}else{
			@OUT=map{sequre($_)}@OUT;
			$page->SplitData("<!--START_RESULT-->","<!--END_RESULT-->");
			$page->replaceINSIDE($q->h1("$LNG{USR_BROWSER_EXPORTED} ".$out->rows." $LNG{USR_BROWSER_PROSPECTS}").join("<BR>\n",@OUT));
		}
	}
	unless($allcount){
		$page->SplitData("<!--START_RESULT-->","<!--END_RESULT-->");
		$page->replaceINSIDE($q->h1($LNG{USR_BROWSER_CANT_EXPORT}));
	}	
	$page->add_regesp('{all_count}',$allcount);
	$page->add_regesp('{account}',$PAR{account});
	$page->add_element("activ","",$LNG{USR_BROWSER_ALL} );
	$page->add_element('activ', 'act', $LNG{USR_BROWSER_ACTIVE});
	$page->add_element('activ', 'dis', $LNG{USR_BROWSER_INACTIVE});
	$page->add_element("format","--email--",$LNG{USR_BROWSER_EXPORT_EMAIL_ONLY});
	$page->add_element("format","--name-- --email--","$LNG{USR_BROWSER_EXPORT_NAME} $LNG{USR_BROWSER_EXPORT_EMAIL}");	
	$page->add_element("format","<--name--> --email--","<$LNG{USR_BROWSER_EXPORT_NAME}> $LNG{USR_BROWSER_EXPORT_EMAIL}");		
	$page->add_element("format","\"--name--\" --email--","\"$LNG{USR_BROWSER_EXPORT_NAME}\" $LNG{USR_BROWSER_EXPORT_EMAIL}");	
	$page->add_element("format","--name--|--email--","$LNG{USR_BROWSER_EXPORT_NAME}|$LNG{USR_BROWSER_EXPORT_EMAIL}");		
	$page->add_element("format","--name--:--email--","$LNG{USR_BROWSER_EXPORT_NAME}:$LNG{USR_BROWSER_EXPORT_EMAIL}");		
	$page->add_element("format","--name--,--email--","$LNG{USR_BROWSER_EXPORT_NAME},$LNG{USR_BROWSER_EXPORT_EMAIL}");			
	$page->add_element("format","--name--TAB--email--","$LNG{USR_BROWSER_EXPORT_NAME}<TAB>$LNG{USR_BROWSER_EXPORT_EMAIL}");
	$page->add_element("to","file",$LNG{USR_BROWSER_EXPORT_FILE});
	$page->add_element("to","here",$LNG{USR_BROWSER_EXPORT_PAGE}); 
	$page->set_def("to","here");
	$page->ParseData;
	return $page->as_string;
}


#######################
sub print_users_bulk{
my $page = new hfparser(
		DATA=>$main_shabl		
	);
	add_menu_prospects($page);	
my @quer;	
if ($PAR{issubmit}){
	@quer=split(/\n/,$PAR{bulk});
	map{s/\s+//g}@quer;
	map{s/\*/%/g}@quer;
	my @QUER;
	foreach(@quer){
		push @QUER, $_ if /[a-zA-Z0-9%.\-_@]/
	}
	unless (@QUER){
		$page->set_error("bulk",$LNG{USR_BROWSER_BULK_QUERY_INCORRECT});
	}
	@quer=map{"(${PREF}user.email LIKE '\%$_\%')"}@QUER;
	my $WHERE;
	if ($PAR{accounts} eq 'all'){
		$WHERE=join(" OR ",@quer);
	}else{
		$WHERE="(".join(" OR ",@quer).") AND fk_account='$PAR{account}'";
	}
	unless ($page->is_error){
		$page->SplitData("#start#user_confirmbulk","#end#user_confirmbulk");
		$page->deleteBEFORE_AFTER;
		$page->add_regesp('{account}',$PAR{account});
		my $sql="SELECT * FROM ${PREF}user WHERE $WHERE";
		my $count=GetSQLCount($sql);
		$page->add_regesp('{countusers}',$count);
		unless($PAR{issubmit2}){
			$page->add_regesp('{status}','will be');
			unless($count){
				$page->SplitData("<!--startdel-->","<!--enddel-->");
				$page->deleteINSIDE;
			}
		}else{	
			$page->add_regesp('{status}','');
			my @users = @{$db->selectcol_arrayref("select pk_user from ${PREF}user WHERE $WHERE")};
			if (@users){
				my $in=join ",",@users;
				$db->do("DELETE FROM ${PREF}user WHERE pk_user IN ($in)");
				&Error;
				$db->do("DELETE FROM ${PREF}doppar WHERE fk_user IN ($in)");
				&Error;
				$db->do("DELETE FROM ${PREF}tosend WHERE fk_user IN ($in)");			
				&Error;
				$db->do("DELETE FROM ${PREF}doiaccounts WHERE fk_user IN ($in)");
				&Error;
				$db->do("DELETE FROM ${PREF}sentlog  WHERE fk_user IN ($in)");
				&Error;
				$db->do("DELETE FROM ${PREF}senthistory  WHERE fk_user IN ($in)");
				&Error;
				$db->do("DELETE FROM ${PREF}link_clicks  WHERE fk_user IN ($in)");
				&Error;
			}
			OPTIMIZEtables();
			$page->SplitData("<!--startdel-->","<!--enddel-->");
			$page->deleteINSIDE;
			
		}
		$page->ParseData;
		return $page->as_string;
	}
}
	$page->SplitData("#start#user_bulk","#end#user_bulk");
	$page->set_default_input("textarea","rows",12);	
	$page->set_default_input("text","size",3);		
	$page->set_default_input("textarea","columns",55);
	unless($PAR{issubmit2}){
		$page->add_element("accounts","this",$LNG{USR_BROWSER_BULK_CURRENT_ACCOUNT});
		$page->add_element("accounts","all",$LNG{USR_BROWSER_BULK_ALL_ACCOUNTS});
	}
	$page->add_regesp('{account}',$PAR{account});
	$page->deleteBEFORE_AFTER;
	$page->ParseData;
	return $page->as_string;
}
sub XMLImport{

return "<BR><BR>".$q->h2("XML import");
}
#######################
sub print_users_import{
	my $page;
	if ($PAR{act4} eq 'xml'){
		return XMLImport();
	}
	unless($PAR{act4} eq 'tab'){
		$page = new hfparser(
			DATA=>$main_shabl,		
			FROM=>"#start#user_import",
			TO=>"#end#user_import"
			);
	}else{
		$page = new hfparser(
			DATA=>$main_shabl,		
			FROM=>"#start#user_tab_import",
			TO=>"#end#user_tab_import"
			);
	}
#	allfields=>\@user_table_fields,
#	names=>\%fields_descr,
#	selected_fields=>\@fields_now,
#	avalible_fields=>\@not_selected
	my $accountfields=GetAllAccountFields($PAR{account},0,{});
	my @import_fields=qw(email name datereg ip);
	my $names=$accountfields->{names};
	$names->{email}=$LNG{FLD_EMAIL};
	$names->{name}=$LNG{FLD_NAME};
	my @add_fields=();
	map{ if (/^field\d+/){push(@import_fields,$_);push(@add_fields,$_)}}@{$accountfields->{allfields}};
	map{$page->add_regesp("{$_}",$PAR{$_})}keys %PAR;
	if($PAR{act4} and $PAR{getsample}){
		print "Content-type: application/octet-stream\nContent-Disposition: attachment; filename=sample.txt\n\n";
		print join("\t",map{$names->{$_}}@import_fields)."\r\n";
		my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
		$year+=1900;
		
		foreach my $n(1..10){
			print join("\t",
				map{
					 /email/ ? 'email'.$n.'@mail.com': /^ip$/ ? "174.23.132.$n":  /^datereg$/ ? "$year-".sprintf("%02d",$mon+1)."-".sprintf("%02d",$mday) :$names->{$_}.$n
				}@import_fields
			)."\r\n";			
		}
		exit;
	}
	#die(join ("|",map{$accountfields->{names}->{$_}}@import_fields));
	my @seq=LoadAccountSequence($PAR{account});		
	if ($PAR{issubmit}){
		unless ($page->is_error){
			my @str;
			
			if ($q->param("uploaded_file")){
				$fh=$q->upload("uploaded_file") || die "$LNG{ERROR_CANT_UPLOAD_FILE} $!";
				@str=<$fh>;	
				chomp(@str);
			}else{
				@str=split(/\n/,$PAR{'import'});
				chomp(@str);
			}
			my $i=0;
			my @errors;
			my $count=0;
			my $SubscrMess;
			if ($CONF{sendsubscr}){
				my $messages=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend=?",$PAR{account},'subscribe');
				$SubscrMess=$messages->{pk_mess};
			}
			my $days;
			my $datelastsend;
			my $messlastsend;
			if($PAR{sequence}==-1){
				#Sequence disabled
				$days=-1;
				$datelastsend='NULL';
				$messlastsend=0;
			}elsif($PAR{sequence}==0){
				$days=0;
				$datelastsend='NULL';
				$messlastsend=0;
			}else{
				$messlastsend=$PAR{sequence};
				map{$days=$_->{days} if $_->{pk_mess} eq $PAR{sequence}}@seq;
				$datelastsend=$NOW;					
			}
			my $updated;
			foreach (@str){
				$i++;
				next unless length $_;
				unless($PAR{act4}){
					#Simple import
					s/([a-zA-Z0-9_.\-]+@[a-zA-Z0-9_.\-]+)//;
					my $mail = lc($1);
					unless ($mail){
						push (@errors, "$LNG{TXT_LINE} $i: $LNG{ERROR_CANT_FIND_EMAIL}");
						next;
					}
					unless (checkemail($mail)){
						push (@errors, "$LNG{TXT_LINE} $i: $LNG{TXT_EMAIL} $mail $LNG{TXT_ISINCORRECT}");
						next;
					}
					if($CONF{useblacklist}){
						if(GetSQLCount("SELECT * FROM ${PREF}bounce_banemails WHERE email=?",$mail)){
							push (@errors, "$LNG{TXT_LINE} $i: $LNG{TXT_EMAIL} $mail $LNG{TXT_IS_BOUNSED}") ;
							next;
						}
					}
					if (GetSQLCount("SELECT * FROM ${PREF}user WHERE email=? AND fk_account=?",$mail,$PAR{account})){
						push (@errors, "$LNG{TXT_LINE} $i: $LNG{TXT_EMAIL} $mail $LNG{TXT_IS_EXISTS}");
						next;
					}
					#s/[^A-Za-z.]/ /g;
					s/[\t><\[\]()\/\\"]/ /g;
					s/^ +//;s/ +$//;
					while (s/  / /g){}
					my @words=split(/ /);
					unless($CONF{no_uppercase}){
						@words=map{ucfirst(lc($_))}@words;
					}
					$name=join(' ',@words);
					$count++;
					$db->do("INSERT INTO ${PREF}user (fk_account,name,email,days,datereg,messlastsend,datelastsend,messageformat) VALUES (?,?,?,?,$NOW,?,$datelastsend,?)",undef,$PAR{account},preparename($name,$CONF{no_uppercase}),prepareemail($mail),$days,$messlastsend,$PAR{messageformat});
					my $maxuser=$db->{'mysql_insertid'};	
					if ($PAR{sendsubscribe}){
						if ($SubscrMess){
							if ($maxuser){
								AddToSend($maxuser,$SubscrMess);
							}
						}
					}
					&Error;
					
				}else{  
					
					next if($i ==1);
					my $existing_user=0;
					#Tab delmitted import
					my ($mail,$name,$datereg, $ip,@fields_values)=split /\t/;
					unless ($mail){
						push (@errors, "$LNG{ERROR} -  $LNG{TXT_LINE} $i: $LNG{ERROR_CANT_FIND_EMAIL}");
						next;
					}
					unless (checkemail($mail)){
						push (@errors, "$LNG{ERROR} -$LNG{TXT_LINE} $i: $LNG{TXT_EMAIL} $mail $LNG{TXT_ISINCORRECT}");
						next;
					}
					if($CONF{useblacklist}){
						if(GetSQLCount("SELECT * FROM ${PREF}bounce_banemails WHERE email=?",$mail)){
							push (@errors, "$LNG{ERROR} - $LNG{TXT_LINE} $i: $LNG{TXT_EMAIL} $mail $LNG{TXT_IS_BOUNSED}") ;
							next;
						}
					}
					my $sr=select_one_db("SELECT * FROM ${PREF}user WHERE email=? AND fk_account=?",$mail,$PAR{account});
					$existing_user=$sr->{pk_user};
					if($existing_user){
						unless($PAR{withexisting}){
							push (@errors, "$LNG{ERROR} - $LNG{TXT_LINE} $i: $LNG{TXT_EMAIL} $mail $LNG{TXT_IS_EXISTS}");
							next;
						}
						push(@updated_list,$mail);						
					}
					if(length($datereg)){
						unless ($datereg=~/^\d\d\d\d-[01]?\d-[0123]?\d$/){
							push (@errors, "$LNG{WARNING} $LNG{TXT_LINE} $i: $LNG{FLD_DATEREG} <B>$datereg</B>".lc($LNG{ERROR_INCORRECT}));
							$datereg="";
						}
					}
					$ip=~s/[^0-9.]//g;
					if(length($ip)){
						my $ReIpNum = qr{([01]?\d\d?|2[0-4]\d|25[0-5])};
						my $ReIpAddr = qr{^$ReIpNum\.$ReIpNum\.$ReIpNum\.$ReIpNum$};
						unless ($ip =~ m{$ReIpAddr}){
							push (@errors, "$LNG{WARNING} $LNG{TXT_LINE} $i: $LNG{FLD_IP} <B>$ip</B> ".lc($LNG{ERROR_INCORRECT})) ;
							$ip="";
						}
					}
					my $dreg=$NOW unless  $datereg;
					$dreg=$db->quote($datereg) if  $datereg;
					my $pk_user;
					unless($existing_user){
						$db->do("INSERT INTO ${PREF}user (fk_account,name,email,days,datereg,messlastsend,datelastsend,messageformat,ip) VALUES (?,?,?,?,$dreg,?,$datelastsend,?,?)",undef,$PAR{account},preparename($name,$CONF{no_uppercase}),prepareemail($mail),$days,$messlastsend,$PAR{messageformat},$ip);	
						&Error("INSERT INTO ${PREF}user (fk_account,name,email,days,datereg,messlastsend,datelastsend,messageformat,ip) VALUES (?,?,?,?,$dreg,?,$datelastsend,?,?) ");						
						$count++;
						$pk_user=$db->{'mysql_insertid'};
						if ($PAR{sendsubscribe}){
							if ($SubscrMess){
								if ($pk_user){
									AddToSend($maxuser,$SubscrMess);
								}
							}
						}
					}else{
						$pk_user=$existing_user;
						my $sql="UPDATE ${PREF}user SET name=? ,datereg = $dreg , messageformat=?, ip=? WHERE pk_user=?";
						$db->do($sql,undef,preparename($name,$CONF{no_uppercase}),$PAR{messageformat}, $ip, $pk_user);
						&Error($sql);
						$updated++;
					}
					foreach my $fieldname(@add_fields){
						my $field_value=shift(@fields_values);
						my $field_id;
						if($fieldname=~/^field(\d+)/){
							$field_id=$1;
						}else{
							next;
						}
						unless(length ($field_value)){
							my $sql="DELETE FROM ${PREF}doppar WHERE fk_fields=? and fk_user=?";
							$db->do($sql,undef,$field_id,$pk_user);
							&Error($sql);
							next;
						}						
						$db->do("REPLACE INTO ${PREF}doppar (fk_fields,fk_user,value) VALUES (?,?,?)",undef,$field_id,$pk_user,$field_value);
						&Error("REPLACE INTO ${PREF}doppar (fk_fields,fk_user,value) VALUES (?,?,?)");
					}
				}
			}
			my $out;
			$out.=$q->h2("$count $LNG{USR_BROWSER_IMPORT_PROSPADD}.") if $count;
			$out.=$q->h2("$updated $LNG{USR_BROWSER_IMPORT_PROSPUPDATED}.") if $updated;
			
			if (@errors){
				$out.=$q->h2(scalar(@errors)." $LNG{USR_BROWSER_IMPORT_ERRORS_DETECTED}");
				$out.=join "<BR>",@errors;
			}
			return $out;
		}
	}
	
	$page->add_element("sequence",0,$LNG{SEQUENCE_STATUS_STARTED});
	my $i=0;
	map{
		$i++;
		$page->add_element("sequence",$_->{pk_mess},"$LNG{USR_SENT_MESSAGE} ".$i." of ".scalar(@seq)." ($LNG{SEQUENCE_DAY_SMALL} $_->{days}) $LNG{SEQUENCE_WAS_SENT}") unless ($i eq scalar(@seq));
		$page->add_element("sequence",$_->{pk_mess},uc($LNG{USR_BROWSER_FINISHED}) ." $LNG{USR_SENT_MESSAGE} ".$i." of ".scalar(@seq)." ($LNG{SEQUENCE_DAY_SMALL} $_->{days}) $LNG{SEQUENCE_WAS_SENT}") if ($i eq scalar(@seq));
	}@seq;
	$page->add_element("withexisting",1,"$LNG{UPDATE}");
	$page->add_element("withexisting",0,"$LNG{SKIP}");
	$page->set_def("withexisting",1);
	$page->add_element("sequence",-1,$LNG{SEQUENCE_STATUS_DISABLED});
	$page->add_element('messageformat','0',$LNG{USR_BROWSER_DEFAULT_FORMAT});
	$page->add_element('messageformat','1',$LNG{USR_BROWSER_TEXT_USER_FORMAT});
	$page->add_element('messageformat','2',$LNG{USR_BROWSER_HTML_USER_FORMAT});
	
	$page->set_default_input("textarea","rows",12);	
	$page->set_default_input("text","size",3);		
	$page->set_default_input("textarea","columns",55);
	$page->set_def("interval",0);
	$page->add_regesp('{account}',$PAR{account});
	$page->ParseData;
	return $page->as_string;
	
}
######################
sub get_insert_link{
	my $value=shift;
	my $name=ucfirst(shift);
	my $mode=shift;
	my $style=qq| class="pers" |;
	unless($mode){
		#text
		return qq|<a $style href="javascript:add_text_mess('$value')" title="$LNG{CLICK_HERE_TO_INSERT}">$name</a>|;
	}elsif($mode==1){
		#html
		$value=qq|<a href=$value>$name</a>| if $value=~/UNSUBSCRIBE_LINK|\[LINK\d+|SUBSCR_ACCOUNT\d+|MODIFY_CONTACT_INFO|RSS_LINK|HTML_LINK/;
		return qq|<a $style href="javascript:add_text_messhtml('$value')" title="$LNG{CLICK_HERE_TO_INSERT}">$name</a>|;
	}elsif($mode==2){
		#rss link
		return qq|<a $style href="javascript:add_text_rss('$value')" title="$LNG{CLICK_HERE_TO_INSERT}">$name</a>|;
	}elsif($mode==9){
		#javascript code
		return qq|<a $style href="javascript:$value" title="Click here to execute this function">$name</a>|;
   }else{
		#Xinha link
		$value=qq|<a href=$value>$name</a>| if $value=~/UNSUBSCRIBE_LINK|\[LINK\d+|SUBSCR_ACCOUNT\d+|MODIFY_CONTACT_INFO|RSS_LINK|HTML_LINK/;
		return qq|<a $style href="javascript:areaedit_editors.messhtml2.insertHTML('$value')" title="$LNG{CLICK_HERE_TO_INSERT}">$name</a>|;
	}
}
sub print_personalize_links{
	my $mode=shift;
	my @FIELDS=map{get_insert_link("[ADD$_->{key}]",$_->{name},$mode)}load_account_fields($PAR{account});
	opendir(DIR,$TempatesDir);
	my @templates=grep{ /\.txt$/ } readdir(DIR);
	closedir(DIR);
	my @FILE_LINKS=();
	foreach(@templates){
		my $fname=$_;
		$fname=~s/\.txt$//;
		push(@FILE_LINKS,get_insert_link("[LOAD_FROM_FILE_$fname]","$LNG{MESS_PERS_LOAD_FROM_FILE} <b>$_</b>",$mode));
	}
	my @SIGNATURES;
	my $sql="SELECT * FROM ${PREF}signatures ORDER by NAME";
	my $out=$db->prepare($sql);
	$out->execute();
	while (my $output=$out->fetchrow_hashref){
		push(@SIGNATURES,get_insert_link("[SIGNATURE_$output->{name}]","$output->{name}",$mode));
	}
	my $sql="SELECT ${PREF}links.pk_link,${PREF}links.name,${PREF}links.redirect_link FROM ${PREF}links LEFT JOIN ${PREF}account ON pk_account=fk_account WHERE pk_account=?";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	my @LINKS;
	while (my $output=$out->fetchrow_hashref){
		push(@LINKS,get_insert_link("[LINK$output->{pk_link}]","<b>$output->{name}</b>",$mode));
	}
	my @main=(
		"<B>$LNG{TAGS_PERSONAL_INFO}:</B> ",
		get_insert_link("[UNSUBSCRIBE_LINK]",$LNG{TAGS_UNSUBSCRIBE_LINK},$mode),
		get_insert_link("[MODIFY_CONTACT_INFO]",$LNG{TAGS_CHANGE_CONTACT_INFO},$mode),
		get_insert_link("[FIRSTNAME]",$LNG{TAGS_FNAME},$mode),
		get_insert_link("[FULLNAME]",$LNG{TAGS_FULLNAME},$mode),
		
		get_insert_link("[FROMNAME]",$LNG{TAGS_FROM_NAME},$mode),
		get_insert_link("[FROMEMAIL]",$LNG{TAGS_FROM_EMAIL},$mode),
		
		get_insert_link("[EMAIL]",$LNG{TAGS_EMAIL},$mode),
		get_insert_link("[DATE]",$LNG{TAGS_DATE},$mode),
		get_insert_link("[REG_DATE]",$LNG{TAGS_REGDATE},$mode),
		get_insert_link("[IP]","IP",$mode),
		get_insert_link("[SUBSCRIBER_ID]",$LNG{PERSONAL_SUBSCRIBER_ID},$mode),
		get_insert_link("[SUBSCRIBER_UUI]",$LNG{PERSONAL_SUBSCRIBER_UUI},$mode),
		get_insert_link("[REFERRER_TRACKING_ID]",$LNG{PERSONAL_REFERRER_TRACKING_ID},$mode),
		"<BR>"
	);
	my @ACTACCOUNTS;
	my $sql="SELECT * FROM ${PREF}account WHERE isact=1 and pk_account<>? ORDER by name";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	while (my $output=$out->fetchrow_hashref){
		push(@ACTACCOUNTS,get_insert_link("[SUBSCR_ACCOUNT$output->{pk_account}]","$output->{name}",$mode));
	}
	@ACTACCOUNTS=("<B>$LNG{TAGS_ONE_CLICK_SUBSCRIBE}:</B> ",@ACTACCOUNTS,"<BR>")if @ACTACCOUNTS;
	@FIELDS=("<B>$LNG{TAGS_CUSTOM_FIELDS}:</B> ",@FIELDS,"<BR>")if @FIELDS;
	@FILE_LINKS=("<B>$LNG{TAGS_TEMPLATES}:</B> ",@FILE_LINKS,"<BR>")if @FILE_LINKS;
	@LINKS=("<B>$LNG{TAGS_LINKTRACK}:</B> ",@LINKS,"<BR>")if @LINKS;
	@SIGNATURES=("<B>$LNG{INSERT_SIGNATURES}:</B> ",@SIGNATURES,"<BR>")if @SIGNATURES;
	my @RSS=();
	@RSS=("<B>$LNG{TAGS_RSS_LINK_DISCR}:</B> ");
	@RSS=(@RSS,get_insert_link("[RSS_LINK]",$LNG{TAGS_RSS_LINK},$mode))if $mode != 2;
	@RSS=(@RSS,get_insert_link("[HTML_LINK]",$LNG{TAGS_HTML_LINK},$mode),"<BR>") ;
   my @HTMLTOTEXT=();
   ############################
   # patch 003 START
	@HTMLTOTEXT=("<B>Replace TEXT with HTML content:</B> ")if $mode == 1;
   @HTMLTOTEXT=(@HTMLTOTEXT,get_insert_link("copyhtmltotext();","Replace omiting HTML tags",9),"<BR>")if $mode == 1;
	# patch003 END
   ############################
	my @L=(@main,@FIELDS,@SIGNATURES,@FILE_LINKS,@LINKS,@ACTACCOUNTS,@RSS,@HTMLTOTEXT);
	return q|<DIV class="perslinks">|.join(" ",@L)."</DIV>";
}
sub print_test_send{
	&printheader;
	my $mess=load_mess($PAR{mess});
	%CONF=loadCONF($PAR{account});
	unless($mess->{pk_mess}){
		print "Your message was not found";
		exit;
	}
	my $page = new hfparser(
		DATA =>"$SHABL_DIR/testsend.html",		
	);
	$page->add_regesp('{header}',$LNG{TEST_SEND_HEADER});
	$page->add_regesp('{subject}',sequre($mess->{subject}));
	if($PAR{issubmit}){
		$page->set_error('email',$LNG{ERROR_EMAIL_INCORRECT})unless(checkemail($PAR{email}));
		unless($page->is_error){
			my $message;
			save_config($PAR{account},'LAST_TEST_SEND_ADDR',$PAR{email});
			$message = $mess->{messhtml} if($PAR{type}=~/html/);
			$message=~s/\[SIGNATURE_([a-zA-Z_0-9]+?)\]/&LoadSignature($1,1)/gse if($PAR{type}=~/html/);
			$message = $mess->{mess} if($PAR{type}=~/text/);
			$message=~s/\[SIGNATURE_([a-zA-Z_0-9]+?)\]/&LoadSignature($1,0)/gse if($PAR{type}=~/text/);
			$message=FillTextFromFile($message);
			$message=FillTextFromURL($message);			
			$msg = new MIME::Lite 
		                From    =>"$CONF{fromname} <$CONF{fromemail}> ",
		                To      =>"$PAR{email}",
		                Subject =>prepare_words($mess->{subject},$mess->{encoding}),
		                Type    =>$TYPESEND{$PAR{type}},
		                Data    =>$message; 
			foreach (keys %{$mess->{ATTACH}}){
				my($mime)=&mimeformat($mess->{ATTACH}{$_}{filename});
				$msg->attach
					(Type =>$mime->[0],
					Encoding =>$mime->[1],
					Id =>"<$mess->{ATTACH}{$_}{filename}>",
					Filename =>$mess->{ATTACH}{$_}{filename},
					Data => $mess->{ATTACH}{$_}{data},
		   		);
			}
			MIMEsendto($PAR{email},$msg);			
			$page->Hide("<!--SENDFORM-->");
			$page->add_regesp('{email}',$PAR{email});
			$page->ParseData;
			$page->print;
			exit;
		}
	}
	$page->Hide('<!--MESSAGESENT-->');
	unless($CONF{LAST_TEST_SEND_ADDR}){
		$page->set_def("email",$CONF{adminemail});
	}else{
		$page->set_def('email',$CONF{LAST_TEST_SEND_ADDR});

	}
	
	$page->set_input("email",{size=>40});
	if ($mess->{type}=~/html/){
		$page->add_element('type', 'html',"HTML");
	}elsif($mess->{type}=~/text/){
		$page->add_element('type', 'text',"Text");
	}else{
		$page->add_element('type', 'text',"Text");
		$page->add_element('type', 'html',"HTML");
	}
	$page->ParseData;
	$page->print;
}
sub print_personalize{
	my @FIELDS=map{"<LI><B>[ADD$_->{key}]</B> - $_->{name}</LI>"}load_account_fields($PAR{account});
	my $page = new hfparser(
		DATA=>$main_shabl,
		FROM=>'#start#personalize',TO=>'#end#personalize'
	);
	my $additional="";
	$additional.="<LI><B>$LNG{MESS_PERS_EXTRA}</b><UL>".join("\n",@FIELDS)."</UL>" if @FIELDS;
	opendir(DIR,$TempatesDir);
	my @templates=grep{ /\.txt$/ } readdir(DIR);
	my @files=();
	map{my $f_name=$_; s/\.txt$//;push(@files,"<LI><B>[LOAD_FROM_FILE_$_]</B> -  $LNG{MESS_PERS_LOAD_FROM_FILE} <b>$f_name</b></LI>")}@templates;
	$additional.="<LI><B>$LNG{MESS_PERS_LOAD_FROM_TEMPL}</b>\n<UL>\n\t".join("\n\t",@files)."\n</UL>" if @templates ;
	my $sql="SELECT ${PREF}links.pk_link,${PREF}links.name,${PREF}links.redirect_link FROM ${PREF}links LEFT JOIN ${PREF}account ON pk_account=fk_account WHERE pk_account=?";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	my @LINKS;
	while (my $output=$out->fetchrow_hashref){
		push(@LINKS,"<LI><B>[LINK$output->{pk_link}] - $LNG{MESS_PERS_REDIR_LINK} <u>$output->{name}</u></B> $LNG{MESS_PERS_REDIR_LINK_TO}  <a href=\"$output->{redirect_link}\" target=\"_blank\">$output->{redirect_link}</a></LI>");
	}
	$additional.="<LI><B>$LNG{MESS_PERS_TRACK}</B>\n</LI>\n<UL>\n\t".join("\n\t",@LINKS)."\n</UL>" if @LINKS;
	my @ACTACCOUNTS;
	my $sql="SELECT * FROM ${PREF}account WHERE isact=1 and pk_account<>? ORDER by name";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	while (my $output=$out->fetchrow_hashref){
		push(@ACTACCOUNTS,"<LI><B>[SUBSCR_ACCOUNT$output->{pk_account}]</B> - subscribe to <i>$output->{name}</i></LI>");
	}
	$additional.="<LI><B>$LNG{TAGS_ONE_CLICK_SUBSCRIBE}:</B></LI>\n<UL>\n\t".join("\n\t",@ACTACCOUNTS)."\n</UL>" if @ACTACCOUNTS;
	$additional.="<LI><B>[REG_DATE]</B> $LNG{PERSONAL_REG_DATE}.</LI>";
	$additional.="<LI><B>[REG_DATE+32d] [REG_DATE-32d] [REG_DATE+1m] [REG_DATE-1m] [REG_DATE+1y] [REG_DATE-1y]</B> $LNG{PERSONAL_REG_DATE_CORRECTED}.</LI>";
	$additional.="<LI><B>[SUBSCRIBER_ID]</B> $LNG{PERSONAL_SUBSCRIBER_ID_DISCR}.</LI>";
	$additional.="<LI><B>[SUBSCRIBER_UUI]</B> $LNG{PERSONAL_SUBSCRIBER_UUI_DISCR}.</LI>";
	$additional.="<LI><B>[MODIFY_CONTACT_INFO]</B> $LNG{PERSONAL_MODIFY_CONTACT_INFO}.</LI>";
	$additional.="<LI><B>[RSS_LINK]</B> $LNG{PERSONAL_RSS_LINK}.</LI>";
	$additional.="<LI><B>[HTML_LINK]</B> $LNG{PERSONAL_HTML_LINK}.</LI>";
	$additional.="<LI><B><font color=\"red\">$LNG{MESS_PERS_NEW}!</font> [REFERRER_TRACKING_ID]</B> $LNG{PERSONAL_REFERRER_TRACKING_ID_DESCR}.</LI>";
	$additional.="<LI><B><font color=\"red\">$LNG{MESS_PERS_NEW}!</font> [SIGNATURE_yoursignature_name]</B> $LNG{PERSONAL_SIGNATURE_DESCR}.</LI>";
	$additional.="<LI><B><font color=\"red\">$LNG{MESS_PERS_NEW}!</font> [LOAD_FROM_URL_http://www.yoursite.com/news.html]</B> $LNG{PERSONAL_LOAD_FROM_URL_DESCR}.</LI>";
	$additional.="\n</UL>\n";

	
	$page->add_regesp('{additional}',$additional);	
	$page->ParseData;
	return $page->as_string;
}
######################
sub print_account_newmess{
	my @req=qw(subject);
	my $page = new hfparser(
		DATA  =>$main_shabl,		
		ERROR_AFTER_TEMPL=>"<SPAN class=\"ERROR_ELEMENT\">&nbsp;&nbsp;&nbsp;&nbsp;###ERR###</SPAN>",
		FROM=>'#start#user_newmess',TO=>'#end#user_newmess'
		
	);
	if ($PAR{issubmit}){
		if($PAR{type} eq 'text' or $PAR{type} eq 'mixed'){
			unless(length($PAR{mess})){
				$page->set_error('type',"TEXT $LNG{ERROR_REQUIRED}");
			}
		}
		if($PAR{type} eq 'html' or $PAR{type} eq 'mixed'){
			unless(length($PAR{messhtml})){
				$page->set_error('type',"HTML $LNG{ERROR_REQUIRED}");
			}
		}
		if($PAR{saveinhistory}){
			push(@req,"messrss");
		}
		if($PAR{usefrom} == 1){
			push(@req,"fromemailmess");
			push(@req,"fromenamemess");
		}		
		foreach (@req){
			$page->set_error($_,$LNG{ERROR_REQUIRED}) if ($PAR{$_} eq '');
		}
		if ($PAR{typesend} eq 'auto'){
			if ($PAR{days}=~/[^0-9]/){
				$page->set_error("days",$LNG{ERROR_NUMBER_REQUIRED});
			}elsif($PAR{days}>2000){
				$page->set_error("days",$LNG{ERROR_TO_BIG});
			}else{
				$page->set_error("days","<NOBR>$LNG{ERROR_ALREADY_USED}<NOBR>") if GetSQLCount("SELECT * FROM ${PREF}mess WHERE fk_account=? and typesend='auto' AND days=? AND pk_mess<>'$PAR{reckey}'",$PAR{account},$PAR{days});
			}
		}
		if ($PAR{typesend} eq 'doi'){
			$page->set_error('mess',"$LNG{MESS_ERR_CONFIRM}: [CONFIRM_URL]") unless ($PAR{mess}=~/\[CONFIRM_URL\]/)
		}		
		if ($PAR{typesend} eq 'senddat'){
			if($PAR{senddat}!~/^\d\d\d\d-\d\d-\d\d$/){
				$page->set_error('senddat',$LNG{ERROR_INCORRECT});
			}else{
				my $corrections=select_one_db("SELECT ? >= CONVERT($NOW,DATE) AS infuture",$PAR{senddat});
				unless($corrections->{infuture}){
					$page->set_error('senddat',$LNG{ERROR_DATE_MUST_BE_IN_FUTURE});
				}
			}
			
		}else{
			$PAR{senddat}="";
			$PAR{repeating}=0;
			
		}
		
		unless ($page->is_error){
			my $id;
			my $days,$datesend;
			$days=0 unless ($PAR{typesend} eq 'auto');
			$days=$PAR{days} if ($PAR{typesend} eq 'auto');
			unless($PAR{reckey}){
				$id=insert_db("${PREF}mess",{
					subject =>$PAR{subject},
					mess=>$PAR{mess} || "",
					messhtml=>$PAR{messhtml} || "",
					defmesstype=>$PAR{defmesstype}||1,					
					type=>$PAR{type},typesend=>$PAR{typesend},
					fk_account=>$PAR{account},days=>$days,
					senddat=>$PAR{senddat},
					priority=>$PAR{priority},
					encoding=>$PAR{encoding},
					saveinhistory=>$PAR{saveinhistory},
					messrss=>$PAR{messrss},
					rsslink=>$PAR{rsslink},
					repeating=>$PAR{repeating},
				       	usefrom=>$PAR{usefrom}, 
					fromnamemess=>$PAR{fromnamemess},  
					fromemailmess=>$PAR{fromemailmess}
					});
			}else{
            ############################
            # Xinha error patch START
            my $messhtml = $PAR{messhtml};
            $messhtml =~ s/%5B/[/g;
            $messhtml =~ s/%5D/]/g;

            my $mess_text = $PAR{mess};
            $mess_text =~ s/%5B/[/g;
            $mess_text =~ s/%5D/]/g;
            # Xinha error patch END
            ############################

				update_db("${PREF}mess",
					{		
					saveinhistory=>$PAR{saveinhistory},
					messrss=>$PAR{messrss},
					subject =>$PAR{subject},
					mess=>$mess_text || "",
					messhtml=>$messhtml || "",
					defmesstype=>$PAR{defmesstype}||1,
					type=>$PAR{type},typesend=>$PAR{typesend},
					fk_account=>$PAR{account},days=>$days,
					senddat=>$PAR{senddat},
					encoding=>$PAR{encoding},
					priority=>$PAR{priority},
					rsslink=>$PAR{rsslink},
					repeating=>$PAR{repeating},
				       	usefrom=>$PAR{usefrom}, 
					fromnamemess=>$PAR{fromnamemess},  
					fromemailmess=>$PAR{fromemailmess}
					},
					{pk_mess=>$PAR{reckey}}
				);
				$id=$PAR{reckey};
			}
			if ($filename=$q->param('uploaded_file')){
				$file=$filename;
				$file=~s(^.*\\)();$file=~s(^.*/)();
				my $data;
				$fh=$q->upload("uploaded_file");
				die ("Can not upload file ".$q->param('uploaded_file')." - not defined filehandle in CGI.pm upload() function $! $@ \n Temp directory is $TempFile::TMPDIRECTORY\n\n") unless $fh;
				binmode($fh);
				my $tmpdata;
				while(sysread $fh,$tmpdata,1024*10){$data.=$tmpdata};
				insert_db("${PREF}attach",{filename=>$file,data=>$data,fk_mess=>$id,len=>length($data)});
			}
			print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&act2=mess&account=$PAR{account}");
			exit();
		}
	}
	my $REPL;
	#DATE
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($MY_TIME);
	$year+=1900;
	$page->add_element("type","text",$LNG{TEXT_ONLY});
	$page->add_element("type","html",$LNG{HTML_ONLY});	
	$page->add_element("type","mixed",$LNG{HTML_AND_TEXT});
	$page->add_element("defmesstype","1","Text");
	$page->add_element("defmesstype","2","HTML");
	$page->add_element("usefrom",0,$LNG{USER_DEFAULT_ACCOUNT_FROM_NAME});
	$page->add_element("usefrom",1,$LNG{OVERRIDE_FROM_NAME_AND_EMAIL});
	$page->add_element("usefrom",2,$LNG{USE_EMAIL_AND_NAME_FROM_PROSPECT_FIELDS});
	$page->add_element("usefrom",3,$LNG{USE_EMAIL_AND_NAME_FROM_REFERRER});
	map{$page->add_element("repeating",$_,$LNG{"REPEAT_MESSAGE_".$_})}(0..4);
	map{$page->add_element('priority',$_,$PRIORITY{$_})}sort keys %PRIORITY;
	$page->add_element('encoding','',$LNG{TXT_DEFAULT});
	map{$page->add_element('encoding',$_,$ENCODINGS{$_});} sort {$ENCODINGS{$a} cmp $ENCODINGS{$b}} keys %ENCODINGS;
	unless($PAR{reckey}){
      ############################
      # patch 002 START - coping attachments
      $page->add_regesp("{header}",$LNG{MESS_CREATE_NEWMESS});
		#$page->add_regesp("{attach}","");
		$page->set_def("encoding",$CONF{'defcharset'});
		map{$page->add_element('typesend',$_,$LNG{"MESS_TYPE_".uc($_)})}qw(manual senddat auto);
		if($PAR{dublicate}){
         my $mess=load_mess($PAR{dublicate});
			
         my $new_id;
         $new_id=insert_db("${PREF}mess",{
					subject =>"New: ".$mess->{subject},
					mess=>$mess->{mess} || "",
					messhtml=>$mess->{messhtml} || "",
					defmesstype=>$mess->{defmesstype}||1,
					type=>$mess->{type},
                                        #typesend=>$mess->{typesend},
					fk_account=>$mess->{account},days=>$days,
					senddat=>$mess->{senddat},
					priority=>$mess->{priority},
					encoding=>$mess->{encoding},
					saveinhistory=>$mess->{saveinhistory},
					messrss=>$mess->{messrss},
					rsslink=>$mess->{rsslink},
					repeating=>$mess->{repeating},
                                        usefrom=>$mess->{usefrom},
					fromnamemess=>$mess->{fromnamemess},
					fromemailmess=>$mess->{fromemailmess}
					});

         foreach (keys %{$mess->{ATTACH}}){
         	my $data_temp = $mess->{ATTACH}{$_}{data};
      		my $file_temp = $mess->{ATTACH}{$_}{filename};

  		      insert_db("${PREF}attach",{filename=>$file_temp,data=>$data_temp,fk_mess=>$new_id,len=>length($data_temp)});
      	}
      	
      	print $q->redirect("$SCRIPT_NAME?reckey=$new_id&ses=$PAR{ses}&act=mainbody&act2=newmess&account=$PAR{account}");
      	# patch 002 END
         ############################
		}
	}else{
		$page->add_regesp("{header}",$LNG{MESS_EDIT_MESS});
		my $mess=load_mess($PAR{reckey});
		map{
			$page->set_def($_,$mess->{$_})
		}qw(senddat days repeating usefrom fromnamemess fromemailmess subject mess messhtml messrss rsslink saveinhistory defmesstype type typesend encoding priority);
		if($mess->{typesend}=~/manual|senddat/){
			map{$page->add_element('typesend',$_,$LNG{"MESS_TYPE_".uc($_)})}qw(manual senddat auto);
		}else{
			$page->add_element('typesend',$mess->{typesend},$LNG{"MESS_TYPE_".uc($mess->{typesend})});
		}
		my @attach=map{
			"<NOBR><a href=\"$SCRIPT_NAME?ses=$PAR{ses}&act=getfile&id=$_\" TITLE=\"$LNG{MESS_DOWNLOAD_ATTACH}\">$mess->{ATTACH}{$_}{filename}</A> (". int($mess->{ATTACH}{$_}{len}/100)/10 ."K)". 
			"&nbsp;&nbsp;&nbsp;<a href=\"$SCRIPT_NAME?ses=$PAR{ses}&act=delfile&id=$_&reckey=$PAR{reckey}&account=$PAR{account}\" >$LNG{DELETE}</a></NOBR>"	
		} keys %{$mess->{ATTACH}};
		my $files=join("<BR>",@attach);
		my $att;
		if ($files){
		$att=<<ALL__;
          <tr> 
            <td align="right"  valign="top"><b>$LNG{MESS_ATTACHMENTS}:</b></td>
            <td >$files</td>
          </tr>
ALL__
		}
		$page->add_regesp("{attach}",$att);
#		$page->add_regesp("{attach}",$mess->{ATTACH});

	}
	$page->add_regesp('{account}',$PAR{account});
	$page->add_regesp('{personalize}',&print_personalize);
	$page->add_regesp('{personal_links}',&print_personalize_links);
	$page->add_regesp('{personal_links_html}',&print_personalize_links(1));
	$page->add_regesp('{personal_links_rss}',&print_personalize_links(2));
	map{$page->set_input("$_", {size=>35})}qw(subject rsslink fromname fromemail);
	$page->set_input("days", {size=>4});
	$page->set_input("mess", {columns=>70,rows=>20,id=>"mess",
		ONSELECT=>"storeCaret(this);",
		ONCLICK=>"storeCaret(this);",
		ONKEYUP=>"storeCaret(this);"});	
	$page->set_input("messhtml", {columns=>70,rows=>20,id=>"messhtml",
		ONSELECT=>"storeCaret(this);",
		ONCLICK=>"storeCaret(this);",
		ONKEYUP=>"storeCaret(this);"});	
	$page->set_input("messrss", {columns=>70,rows=>8,id=>"messrss",
		ONSELECT=>"storeCaret(this);",
		ONCLICK=>"storeCaret(this);",
		ONKEYUP=>"storeCaret(this);"});	
	$page->add_regesp('{radio_autorespond}',$q->radio_group(-default=>$PAR{typesend},-name=>'typesend',-values=>['auto'],-labels=>{auto=>$LNG{MESS_TYPE_AUTO}}));
	$page->add_regesp('{radio_manual}',$q->radio_group     (-default=>$PAR{typesend},-name=>'typesend',-values=>['manual'],-labels=>{manual=>$LNG{MESS_TYPE_MANUAL}}));
	$page->add_regesp('{radio_sendatdate}',$q->radio_group (-default=>$PAR{typesend},-name=>'typesend',-values=>['senddat'],-labels=>{senddat=>$LNG{MESS_TYPE_SCHEDULED}}));
	$page->ParseData;
	return $page->as_string;
}
sub print_change_editor{
	
}
sub print_show_mess{
	&printheader;
	my $mess=load_mess($PAR{mess});
	%CONF=loadCONF($PAR{account});
	my $page = new hfparser(
		DATA =>"$SHABL_DIR/preview.html",		
	);
	if($mess->{type}=~/mixed/i and !$PAR{messformat}){
		$page->add_regesp('{subject}',sequre($LNG{PLEASE_CHOICE_FOFMAT}));
		$q->param('messformat','text');
		my $text_url=$q->self_url;
		$q->param('messformat','html');
		my $html_url=$q->self_url;
		$page->add_regesp('{mess}',qq|\n<UL>\n<LI><a href="$html_url">$LNG{MSG_HTML_FORMAT}</A></LI>\n<LI><a href="$text_url">$LNG{MSG_TEXT_FORMAT}</A>\n</LI>\n<UL>|);
		$page->ParseData;
		$page->print;
		exit;
	}
	if($mess->{type}=~/html/i or ($PAR{messformat} eq 'html')){
		$messtext=$mess->{messhtml};
		$messtext=FillTextFromFile($messtext);
		$messtext=FillTextFromURL($messtext);
		$messtext=~s/\[SIGNATURE_([a-zA-Z_0-9]+?)\]/&LoadSignature($1,1)/gse;
		print $messtext;
		return;
	}
	$messtext=$mess->{mess};
	$messtext=FillTextFromFile($messtext);
	$messtext=FillTextFromURL($messtext);
	$messtext=~s/\[SIGNATURE_([a-zA-Z_0-9]+?)\]/&LoadSignature($1,0)/gse;
	$page->add_regesp('{subject}',sequre($mess->{subject}));
	$page->add_regesp('{mess}',sequre($messtext));
	$page->add_regesp('{link}',
		$q->a({-href=>get_full_url({act=>'showrfcmess'})},'Switch to RFC mode')
	);
	$page->ParseData;
	$page->print;
}

######################
sub print_getfile{
	my $sql="SELECT * from ${PREF}attach WHERE pk_attach=?";
	my $out=$db->prepare($sql);
	$out->execute($PAR{id});
	&Error;
	$output=$out->fetchrow_hashref;
	print "Content-type: application/octet-stream\nContent-Disposition: attachment; filename=$output->{filename}\n\n";
	binmode(STDOUT);
	print $output->{data};
	exit();
}
######################
sub print_delfile{
	$db->do("DELETE FROM ${PREF}attach WHERE pk_attach=?",undef,$PAR{id});
	print $q->redirect("$SCRIPT_NAME?act=mainbody&account=$PAR{account}&act2=newmess&reckey=$PAR{reckey}&ses=$PAR{ses}");
	exit(1);
}
######################
######################
sub print_doimess{
	my $mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='doi'",$PAR{account});
	unless ($mess->{pk_mess}){
		my $MESS=<<ALL__;
$LNG{DOI_MESS}
ALL__
		insert_db("${PREF}mess",{mess=>"$MESS",subject=>"Please confirm your subscription",fk_account=>$PAR{account},typesend=>'doi'});	
		$mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='doi'",$PAR{account});
	}
	if ($PAR{act2} eq "preview"){
		print $q->redirect("$SCRIPT_NAME?act=showmess&account=$PAR{account}&mess=$mess->{pk_mess}&ses=$PAR{ses}");
	}else{
		print $q->redirect("$SCRIPT_NAME?act=mainbody&account=$PAR{account}&act2=newmess&reckey=$mess->{pk_mess}&ses=$PAR{ses}");
	}
	exit(1);
}
######################
sub print_subsmess{
	my $mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='subscribe'",$PAR{account});
	unless ($mess->{pk_mess}){
		insert_db("${PREF}mess",{mess=>"Your message",subject=>"Subscribe message",fk_account=>$PAR{account},typesend=>'subscribe'});	
		$mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='subscribe'",$PAR{account});
	}
	if ($PAR{act2} eq "preview"){
		print $q->redirect("$SCRIPT_NAME?act=showmess&account=$PAR{account}&mess=$mess->{pk_mess}&ses=$PAR{ses}");
	}else{
		print $q->redirect("$SCRIPT_NAME?act=mainbody&account=$PAR{account}&act2=newmess&reckey=$mess->{pk_mess}&ses=$PAR{ses}");
	}
	exit(1);
}
#######################
sub print_unsubsmess{
	my $mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='unsubscribe'",$PAR{account});
	unless ($mess->{pk_mess}){
		insert_db("${PREF}mess",{mess=>"Your message",subject=>"Unsubscribe message",fk_account=>$PAR{account},typesend=>'unsubscribe'});	
		$mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='unsubscribe'",$PAR{account});
	}
	if ($PAR{act2} eq "preview"){
		print $q->redirect("$SCRIPT_NAME?act=showmess&account=$PAR{account}&mess=$mess->{pk_mess}&ses=$PAR{ses}");
	}else{
		print $q->redirect("$SCRIPT_NAME?act=mainbody&account=$PAR{account}&act2=newmess&reckey=$mess->{pk_mess}&ses=$PAR{ses}");
	}
	exit(1);
}
########################
sub sendtoadmin{
my $to = shift;
my $messid=shift;
my $mess=load_mess($messid);
   	$msg = new MIME::Lite 
                From    =>"$CONF{fromname} <$CONF{fromemail}> ",
                To      =>"$to",
                Subject =>$mess->{subject},
                Type    =>$TYPESEND{$mess->{type}},
                Data    =>$mess->{mess}; 
	foreach (keys %{$mess->{ATTACH}}){
		my($mime)=&mimeformat($mess->{ATTACH}{$_}{filename});
		$msg->attach
			(Type =>$mime->[0],
			Encoding =>$mime->[1],
			Id =>"<$mess->{ATTACH}{$_}{filename}>",
			Filename =>$mess->{ATTACH}{$_}{filename},
			Data => $mess->{ATTACH}{$_}{data},
   		);
	}
	MIMEsendto($to,$msg);
}
sub preparetodeleteauto{
	my $messid=shift;
	my @messages = @{$db->selectcol_arrayref("select pk_mess from ${PREF}mess WHERE fk_account=$PAR{account} AND  typesend = 'auto' ORDER by days ASC")};
	&Error;
	$i=0;
	my %mess;
	foreach (@messages){
		$mess{$_}=$i;
		$i++;
	}
	my $newmess;
	if ($mess{$messid}==0){
		$newmess='NULL';
	}else{
		$newmess=$messages[$mess{$messid}-1];
	}
	$db->do("UPDATE ${PREF}user SET messlastsend=$newmess WHERE messlastsend='$messid'");
	&Error;
}
#######################
sub get_test_send_link{
	my $mess=shift;
	my $link="$SCRIPT_NAME?ses=$PAR{ses}&act=testsend&account=$PAR{account}&mess=$mess->{pk_mess}";
	return (qq|<a href="$link" target="_blank"onClick="window.open('$link','','scrollbars=yes,resizable=yes,width=550,height=300'); return false;">$LNG{TEST_SEND_LINK}</a>|);
}
#######################
sub print_edit_cycle{
	my $page = new hfparser(
		DATA=>$main_shabl,FROM=>"#start#mess_seq_cycle",TO=>"#end#mess_seq_cycle"
	);
	my @fields=qw(seqcycle_enabled seqcycle_days seqcycle_startmess seqcycle_maxrepeat);
	if($PAR{issubmit}){
		if($PAR{seqcycle_enabled}){
			if(length($PAR{seqcycle_days}) and $PAR{seqcycle_days}=~/[^0-9]/){
				$page->set_error('seqcycle_days',$LNG{ERROR_NUMBER_REQUIRED});
			}
			if(length($PAR{seqcycle_maxrepeat}) and $PAR{seqcycle_maxrepeat}=~/[^0-9]/){
				$page->set_error('seqcycle_maxrepeat',$LNG{ERROR_NUMBER_REQUIRED});
			}			
		}
		unless($page->is_error){
			map{save_config($PAR{account},$_,$PAR{$_})}@fields;
			print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=$PAR{act}&account=$PAR{account}&act2=$PAR{act2}");
			exit;			
		}
		
	}
	my @seq=LoadAccountSequence($PAR{account});
	my $i=0;
	map{
		$i++;
		$page->add_element("seqcycle_startmess",$_->{pk_mess},"$LNG{USR_SENT_MESSAGE} ".$i." of ".scalar(@seq)." ($LNG{SEQUENCE_DAY_SMALL} $_->{days})");
	}@seq;
	#%CONF=loadCONF($PAR{account});
	map{
		$page->set_def($_,$CONF{$_});
	}@fields;
	$page->ParseData();
	return $page->as_string;
}
#######################
sub print_account_mess{
	return print_edit_cycle() if($PAR{editcycle});
	my $page = new hfparser(
		DATA=>$main_shabl		
	);
	$page->add_regesp('{start_broadcast}',"");
	if ($PAR{bnsettings}){
		save_config($PAR{account},"sendsubscr",$PAR{sendsubscr});
		save_config($PAR{account},"sendunsubscr",$PAR{sendunsubscr});		
		save_config($PAR{account},"isdoi",$PAR{isdoi});
	}elsif($PAR{bnRemoveAuto}){
		my @elements=$q->param('selauto');
		foreach (@elements){
			preparetodeleteauto($_);
			$db->do("DELETE FROM ${PREF}mess WHERE pk_mess='$_'");
		}
		$db->do("DELETE FROM ${PREF}attach WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}tosend WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}sentlog  WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}senthistory  WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}link_clicks  WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;		
	}elsif($PAR{bnRemoveDate}){
		my @elements=$q->param('seldate');
		$db->do("DELETE FROM ${PREF}mess WHERE pk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}attach WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}tosend WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}sentlog  WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		$db->do("DELETE FROM ${PREF}senthistory  WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;		
		$db->do("DELETE FROM ${PREF}link_clicks  WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
	}elsif($PAR{bnBroadkast}){
		$page->add_regesp('{start_broadcast}',"<h1 class=\"mess\">$LNG{MESS_BROADCAST_STARTED}</h1><img src=\"$CONF{serverurl}starter.cgi\" width=\"2\" height=\"2\"> ");
		my @elements=$q->param('seldate');
		if (@elements){
			$db->do("UPDATE ${PREF}mess set issendnow=1 WHERE pk_mess IN(".join(" , ",@elements).")");			
			&Error;
		}
	}elsif($PAR{bnClearTosent}){
		my @elements=$q->param('selsent');
		if (@elements){
			$db->do("DELETE FROM ${PREF}tosend WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		}
	}elsif($PAR{bnMoveNotSent}){
		my @elements=$q->param('selsent');
		my $mess;
		$db->do("DELETE FROM ${PREF}tosend WHERE fk_mess IN (".join(" , ",@elements).")") if @elements;
		foreach  $mess(@elements){
			update_db("${PREF}mess",{typesend=>'manual',senddat=>''},{pk_mess=>$mess});
		}
	}elsif($PAR{SEND}){
		$page->set_error("sendto",$LNG{ERROR_EMAIL_INCORRECT}) unless (checkemail($PAR{sendto},0));	
		unless ($page->is_error()){
			my @elements=$q->param('selsent');
			@elements=(@elements,$q->param('seldate'));
			@elements=(@elements,$q->param('selauto'));		
			foreach (@elements){
				sendtoadmin($PAR{sendto},$_);
			}
		}
	}elsif($PAR{addnewmess} or $PAR{addnewmessmanual}){
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&account=$PAR{account}&act=mainbody&act2=newmess&typesend=manual");
		exit;
	}elsif($PAR{addnewmessseq}){
		print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&account=$PAR{account}&act=mainbody&act2=newmess&typesend=auto");
		exit;
	}
	my $cycle_mess="$LNG{DISABLED}";
	if($CONF{seqcycle_enabled}){
		$cycle_mess=qq|<FONT color="green">$LNG{CYCLE_ACTIVATED}</FONT>|;
			
	}
	$page->add_regesp('{SEQUENCE_CYCLE_STATUS}',$cycle_mess);
	
        my $messtosend = GetSQLCount("SELECT * FROM ${PREF}mess WHERE fk_account=? and typesend<>'subscribe' AND typesend<>'subscribe'",$PAR{account});	
	unless($messtosend){
		$page->SplitData("<!--START_SENDTO-->","<!--END_SENDTO-->");
		$page->replaceINSIDE("");
	}
	map{
		my $my_mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? and typesend='$_'",$PAR{account});
		if ($my_mess->{pk_mess}){
			$page->add_regesp("{test_send_$_}",get_test_send_link($my_mess));

		}else{
			$page->add_regesp("{test_send_$_}","");
		}		
	}qw(doi subscribe unsubscribe);
	$page->SplitData("#start#user_mess","#end#user_mess");
	$page->deleteBEFORE_AFTER();
	my $mess_act="<font color=green>$LNG{MESS_ACTIVE}</font>";
	my $mess_inact="<font color=red>$LNG{MESS_INACTIVE}</font>";
	if($CONF{sendsubscr}){
		$page->add_regesp('{STATUS_SUBSCRIBE}',$mess_act);
	}else{
		$page->add_regesp('{STATUS_SUBSCRIBE}',$mess_inact);
	}
	if($CONF{sendunsubscr}){
		$page->add_regesp('{STATUS_UNSUBSCRIBE}',$mess_act);
	}else{
		$page->add_regesp('{STATUS_UNSUBSCRIBE}',$mess_inact);
	}	
	if($CONF{isdoi}){
		$page->add_regesp('{STATUS_DOI}',$mess_act);
	}else{
		$page->add_regesp('{STATUS_DOI}',$mess_inact);
	}
	map{$page->add_regesp("{".$_."}",$PAR{$_})}qw(account act act2 act3);
	map{
		if(GetSQLCount("SELECT * FROM ${PREF}mess WHERE typesend='$_' and fk_account=? and saveinhistory is not NULL",$PAR{account})){
			$page->add_regesp("{RSS_IMAGE_".uc($_)."}","content.cgi?get=image&mode=gif&f=rss");
		}else{
			$page->add_regesp("{RSS_IMAGE_".uc($_)."}","content.cgi?get=image&mode=gif&f=sp");
		}
	}qw(doi subscribe unsubscribe);
	$page->set_def("sendsubscr",$CONF{sendsubscr});	
	$page->set_def("sendunsubscr",$CONF{sendunsubscr});	
	$page->set_def("isdoi",$CONF{isdoi});
	#############
	$automessages=GetSQLCount("SELECT * FROM ${PREF}mess WHERE fk_account=? and typesend='auto'",$PAR{account});
	$page->add_regesp('{autocount}',$automessages);
	if ($automessages){
		my $sql="SELECT * FROM ${PREF}mess WHERE fk_account=? and typesend='auto' ORDER by days ASC";
		my $out=$db->prepare($sql);
		$out->execute($PAR{account});
		&Error;
		my $Auto;
		while (my %output=%{$out->fetchrow_hashref}){
			map{$output{$_}=sequre($output{$_})}keys %output;
			my $attach=load_mess_attachment($output{pk_mess});
			my @att=map{"<NOBR><a href=\"$SCRIPT_NAME?ses=$PAR{ses}&act=getfile&id=$_\">$attach->{$_}{filename}(". int(length($attach->{$_}{data})/100)/10 ."K)</A></NOBR>"} keys %$attach;
			my $att=join " ",@att;
			my $rss_image;
			if($output{saveinhistory}){
				$rss_image="img/rss.gif";
			}else{
				$rss_image="img/sp.gif";
			}
			my $test_send_link=get_test_send_link(\%output);
			$Auto.=<<ALL__;
	  <tr class="data"> 
	    <td  ><INPUT type="checkbox" name="selauto" value="$output{pk_mess}"></td>
	  <td  width="16" ><a title="$LNG{DUBLICATE_MESSAGE}" href="$SCRIPT_NAME?dublicate=$output{pk_mess}&ses=$PAR{ses}&act=mainbody&act2=newmess&account=$PAR{account}&typesend=auto"><img src="content.cgi?get=image&mode=png&f=editcopy" width="16" height="16" border="0" alt="$LNG{DUBLICATE_MESSAGE}"></a></td>  
	  <td  width="25" ><img src="$rss_image" width="25" height="13" border="0"></td>
	    <td width="99%" >
	    <a href="$SCRIPT_NAME?reckey=$output{pk_mess}&ses=$PAR{ses}&act=mainbody&act2=newmess&account=$PAR{account}">$output{subject}</a>
	    </td>
	    <td  >$output{type}</td>
	    <td  >$att</td>
	    <td  align="center">$output{sent}</td>
	    <td  align="center">$output{days}</td>
	    <td><a target="_blank" href="$SCRIPT_NAME?ses=$PAR{ses}&act=showmess&mess=$output{pk_mess}&account=$PAR{account}"
	    onClick="window.open('$SCRIPT_NAME?ses=$PAR{ses}&act=showmess&mess=$output{pk_mess}&account=$PAR{account}','','scrollbars=yes,resizable=yes,width=650,height=550'); return false;"	    
	    >$LNG{MESS_PREVIEW}</a></td>
	    <td>$test_send_link</td>
	  </tr>
ALL__
		}
		$page->add_regesp("<!--AUTOMESS-->",$Auto);
		$page->Hide('<!--NOMESS-->');

	}else{
		$page->Hide("<!--START_AUTO-->","<!--END_AUTO-->");
	}
	################	
	$datemessages=GetSQLCount("SELECT * FROM ${PREF}mess WHERE fk_account=? and (typesend='senddat' OR typesend='manual' OR typesend='sent')",$PAR{account});
	$page->add_regesp('{datecount}',$datemessages);
	if ($datemessages){
		my $sql="SELECT ${PREF}mess.* , DATE_FORMAT(senddat, '%Y-%b-%d' ) as senddat FROM ${PREF}mess WHERE fk_account=? and (typesend='senddat' OR typesend='manual' OR typesend='sent') ORDER by senddat ASC";
		my $out=$db->prepare($sql);
		$out->execute($PAR{account});
		my $Auto;
		while (my %output=%{$out->fetchrow_hashref}){
			map{$output{$_}=sequre($output{$_})}keys %output;
			my $attach=load_mess_attachment($output{pk_mess});
			my @att=map{"<NOBR><a href=\"$SCRIPT_NAME?ses=$PAR{ses}&act=getfile&id=$_\">$attach->{$_}{filename}(". int(length($attach->{$_}{data})/100)/10 ."K)</A></NOBR>"} keys %$attach;
			my $att=join " ",@att;
			my $test_send_link=get_test_send_link(\%output);
			my $tosent=GetSQLCount("SELECT * FROM ${PREF}tosend WHERE fk_mess=?",$output{pk_mess});
			my $rss_image;
			if($output{saveinhistory}){
				$rss_image="img/rss.gif";
			}else{
				$rss_image="img/sp.gif";
			}
			my $repeating;
			if($output{typesend} eq 'senddat' and $output{repeating}){
				$repeating="<BR><NOBR><i>(".$LNG{"REPEAT_MESSAGE_$output{repeating}"}.")</i></NOBR>";
			}
			$Auto.=<<ALL__;
	  <tr class="data"> 
	    <td  ><INPUT type="checkbox" name="seldate" value="$output{pk_mess}"></td>
	  <td  width="16" ><a title="$LNG{DUBLICATE_MESSAGE}" href="$SCRIPT_NAME?dublicate=$output{pk_mess}&ses=$PAR{ses}&act=mainbody&act2=newmess&account=$PAR{account}&typesend=auto"><img src="content.cgi?get=image&mode=png&f=editcopy" width="16" height="16" border="0" alt="$LNG{DUBLICATE_MESSAGE}"></a></td>
	  <td  width="25" ><img src="$rss_image" width="25" height="13" border="0"> </td>	    
	    <td width="99%">
	    	<a href="$SCRIPT_NAME?reckey=$output{pk_mess}&ses=$PAR{ses}&act=mainbody&act2=newmess&account=$PAR{account}">$output{subject}</a>
	    </td>
	    <td>$output{type}</td>
	    <td  >$att</td>
	    <td  align="center"><NOBR>$output{senddat}$repeating</NOBR></td>
	    <td  align="center">$tosent</td>
	    <td  align="center">$output{sent}</td>	    
	    <td><a target="_blank" href="$SCRIPT_NAME?ses=$PAR{ses}&act=showmess&mess=$output{pk_mess}&account=$PAR{account}"
	    onClick="window.open('$SCRIPT_NAME?ses=$PAR{ses}&act=showmess&mess=$output{pk_mess}&account=$PAR{account}','','scrollbars=yes,resizable=yes,width=650,height=550'); return false;"	    
	    >$LNG{MESS_PREVIEW}</a></td>
	    <td>$test_send_link</td>
	  </tr>
ALL__
		}
		$page->add_regesp("<!--DATEMESS-->",$Auto);
		$page->Hide('<!--NOMESS-->');

	}else{
		$page->Hide("<!--START_DATE-->","<!--END_DATE-->");
	}
	$page->set_def("sendto",$CONF{adminemail});	
	$page->add_regesp('{account}',$PAR{account});

	$page->ParseData;
	return $page->as_string;
}
sub print_changelink{
	my $page=new hfparser (
		DATA=>$links_shabl,
		FROM=>'#start#formlinks',TO=>'#end#formlinks'
	);
	my $link;
	my $is_new;
	if($PAR{id}){
		$link=select_one_db("SELECT * FROM ${PREF}links WHERE pk_link=?",$PAR{id});
		unless($link->{pk_link}){
			$PAR{id}="";
			$page->Hide('<!--hideifnew-->');	
			$is_new=1;
		}else{
			$is_new=0;
			$page->add_regesp('{name_link}',$link->{name});
			$page->set_def('name',$link->{name});
			$page->set_def('url',$link->{redirect_link});
			$page->Hide('<!--hideifedit-->');
		}
	}else{
		$page->Hide('<!--hideifnew-->');		
		$page->set_def('url','http://');
		$is_new=1;
	}
	if($PAR{issubmit}){
		map{$page->set_error($_,$LNG{ERROR_REQUIRED}) unless(length $PAR{$_})}qw(name url);
		$page->set_error('url',$LNG{ERROR_URL_INCORRECT}) unless check_url($PAR{url});
		unless($page->is_error){
			if($is_new){
				insert_db("${PREF}links",{name=>$PAR{name},redirect_link=>$PAR{url},fk_account=>$PAR{account}});
				&Error;
			}else{
				update_db("${PREF}links",{name=>$PAR{name},redirect_link=>$PAR{url}},{pk_link=>$PAR{id}});
			}
			print $q->redirect("$SCRIPT_NAME?act=$PAR{act}&account=$PAR{account}&act2=links&ses=$PAR{ses}");
			exit;				
		}
	}
	$page->ParseData;
	return $page->as_string;	
}
sub prepare_long_name{
	my $txt=shift;
	if (length($txt)>25){
		return substr($txt,0,25)."...";
	}else{
		return $txt;
	}
}
sub print_links_mesrospects{
	my $is_prospects=shift;
	my $page= new repparser(
		DATA=>$links_shabl,
		FROM=>'#start#prospects',TO=>'#end#prospects'
	);
	$page->set_input("emailsearch", {size=>25});
	if ($is_prospects){
		$page->Hide('<!--IS_CLICKS-->');
	}else{
		$page->Hide('<!--IS_PROSPECTS-->');
	}
	my $out1=$db->prepare("SELECT DISTINCT DATE_FORMAT( timestamp, '%M, %Y' ) as m FROM `${PREF}link_clicks` LEFT JOIN ${PREF}mess ON pk_mess = fk_mess WHERE ${PREF}mess.fk_account=?") ;
	$out1->execute($PAR{account});
	$page->add_element('dateselect','',$LNG{LINKS_ALL_MONTH});
	while (my $row=$out1->fetchrow_hashref){
		$page->add_element('dateselect',$row->{m},$row->{m});
	}
	my $out1=$db->prepare("SELECT pk_mess, subject  FROM `${PREF}link_clicks` LEFT JOIN ${PREF}mess ON pk_mess = fk_mess WHERE ${PREF}mess.fk_account=? GROUP by pk_mess") ;
	$out1->execute($PAR{account});
	$page->add_element('message','',$LNG{LINKS_ALL_MESS});
	&Error;
	while (my $row=$out1->fetchrow_hashref){
		$page->add_element('message',$row->{pk_mess},prepare_long_name($row->{subject}));
	}
	my $out1=$db->prepare("SELECT ${PREF}links.pk_link as pk_link, ${PREF}links.name AS name, redirect_link as url   FROM `${PREF}link_clicks` LEFT JOIN ${PREF}mess ON pk_mess = fk_mess 
		LEFT JOIN ${PREF}links ON fk_link=pk_link
		WHERE ${PREF}mess.fk_account=? GROUP by pk_link") ;
	$out1->execute($PAR{account});
	$page->add_element('link','',$LNG{LINKS_ALL_LINKS});
	&Error;
	while (my $row=$out1->fetchrow_hashref){
		$page->add_element('link',$row->{pk_link},prepare_long_name("$row->{name} ($row->{url})"));
	}
	my @WHERE;
	push @WHERE,"${PREF}mess.fk_account=?";
	push(@WHERE,'DATE_FORMAT( '.$PREF.'link_clicks.timestamp, \'%M, %Y\' ) = '.$db->quote($PAR{dateselect})) if($PAR{dateselect});
	push(@WHERE,"pk_mess=".$db->quote($PAR{message})) if $PAR{message};
	push(@WHERE,"pk_link=".$db->quote($PAR{'link'})) if $PAR{'link'};
	push(@WHERE,"email LIKE(".$db->quote('%'."$PAR{'emailsearch'}".'%').")") if $PAR{'emailsearch'};

	my $where="WHERE ".join("\n AND ",@WHERE) if @WHERE;
	my $sql;
	if($is_prospects){
	$sql=<<ALL__;
	SELECT 
		${PREF}user.email as email,
		${PREF}user.pk_user as pk_user,
		${PREF}user.name as name,
		count(pk_link_click) as clicks
	FROM `${PREF}link_clicks` 
		LEFT JOIN ${PREF}mess ON pk_mess = fk_mess 
		LEFT JOIN ${PREF}links ON fk_link=pk_link
		LEFT JOIN ${PREF}user ON fk_user=pk_user
	$where  
	GROUP by pk_user
	ORDER BY clicks
ALL__
}else{
	$sql=<<ALL__;
	SELECT 
		DATE_FORMAT(${PREF}link_clicks.timestamp , \'%d/%m/%Y %H:%i\' ) as date,
		${PREF}user.email as email,
		${PREF}user.pk_user as pk_user,
		${PREF}user.name as name,
		1 as clicks
	FROM `${PREF}link_clicks` 
		LEFT JOIN ${PREF}mess ON pk_mess = fk_mess 
		LEFT JOIN ${PREF}links ON fk_link=pk_link
		LEFT JOIN ${PREF}user ON fk_user=pk_user
	$where  
	ORDER BY ${PREF}link_clicks.timestamp
ALL__

}
	my $out1=$db->prepare($sql) ;
	$out1->execute($PAR{account});
	&Error($sql);
	my $total_clicks=0;
	while (my $row=$out1->fetchrow_hashref){
		$row->{url_search}=get_links_stat_link('clicks',$PAR{message},$PAR{'link'},$row->{email});
		if($row->{pk_user}){
			$row->{url}=qq|<a href="$SCRIPT_NAME?ses=$PAR{ses}&account=$PAR{account}&act=mainbody&act2=userform&reckey=$row->{pk_user}">$LNG{TXT_VIEW}&gt;&gt;&gt;</a>|;
		}else{
			$row->{url}="&nbsp;";
		}
		$page->AddRow($row);
		$total_clicks+=$row->{clicks};
	}
	$page->add_regesp('{total_clicks}',$total_clicks);

	$page->ParseData;
	return $page->as_string;
}
sub print_links_mess{
	my $where;
	if ($PAR{dateselect}){
		$where=' AND DATE_FORMAT( timestamp, \'%M, %Y\' ) LIKE '.$db->quote($PAR{dateselect});
	}
	my $sql=<<ALL__;
SELECT 
	fk_mess AS messID, 
	IFNULL( subject, 'Unknown message' ) AS subject, 
	IFNULL( ${PREF}links.name, 'Unknown link' ) AS linkname, 
	redirect_link AS url, 
	fk_link AS linkID, 
	COUNT( pk_link_click ) AS clicks, 
	COUNT( DISTINCT fk_user ) AS prospects
FROM `${PREF}link_clicks` 
LEFT JOIN ${PREF}mess ON pk_mess = fk_mess
LEFT JOIN ${PREF}links ON pk_link = fk_link
WHERE ${PREF}mess.fk_account=? $where
GROUP BY fk_mess, fk_link
ORDER BY fk_mess, fk_link
ALL__
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	return qq|<h1 class="mess" align="center">No logs found</h1>| unless $out->rows();
	 my $sql=<<ALL__;
SELECT 
	fk_mess AS messID, 
	COUNT( DISTINCT fk_user ) AS prospects
FROM `${PREF}link_clicks` 
LEFT JOIN ${PREF}mess ON pk_mess = fk_mess
WHERE ${PREF}mess.fk_account=? $where
GROUP BY fk_mess
ALL__
	my %mess;
 	my $out2=$db->prepare($sql);
	$out2->execute($PAR{account});	
	while(my $row=$out2->fetchrow_hashref){
		$mess{$row->{messID}}[1]=$row->{prospects};
	}
	my $page=new hfparser(
		DATA=>$links_shabl,
		FROM=>'#start#statmess',TO=>'#end#statmess'
	);
	my $out1=$db->prepare("SELECT DISTINCT DATE_FORMAT( timestamp, '%M, %Y' ) as m FROM `${PREF}link_clicks` LEFT JOIN ${PREF}mess ON pk_mess = fk_mess WHERE ${PREF}mess.fk_account=?") ;
	$out1->execute($PAR{account});
	$page->add_element('dateselect','',$LNG{LINKS_ALL_MONTH});
	while (my $row=$out1->fetchrow_hashref){
		$page->add_element('dateselect',$row->{m},$row->{m});
	}
	my $add;
	$add=" ($PAR{dateselect})" if ($PAR{dateselect});
	my $ouput=<<ALL__;
	<h2>$LNG{LINKS_MESSAGES_LINKS_ACT}$add</h2><br>
	<table width=90% align="center" cellpadding="2" cellspacing="0">
		<TR class = dataheader>
			<TD>$LNG{USR_SENT_MESSAGE}</TD>
			<TD>$LNG{ACCOUNTMENU_LINK}</TD>
			<TD align=right>$LNG{STATMENU_TOTALS_PROSPECTS}</TD>
			<TD align=right>$LNG{CLICKS}</TD>
		</TR>
ALL__
	my $messnow=undef;
	my $totalClicks=0;
	while (my $row=$out->fetchrow_hashref){
		if($row->{messID} != $messnow){
		my $l_p=get_links_stat_link('prospects',$row->{messID},undef);
		my $l_c=get_links_stat_link('clicks',$row->{messID},undef);
		$ouput.=<<ALL__;
			<TR class=data2>
				<TD colspan=2><B>$row->{subject}</B></TD>
				<TD align=right><B>$mess{$row->{messID}}[1]<a href="$l_p" title="$LNG{LINKS_VIEW_PROSP}">...</a></B></TD>
				<TD align=right><B>###CL$row->{messID}#<a href="$l_c" title="$LNG{LINKS_VIEW_CLICKS}">...</a></B></TD>
</TR>
ALL__
		$messnow=$row->{messID};
		}
		my $l_p=get_links_stat_link('prospects',$row->{messID},$row->{linkID});
		my $l_c=get_links_stat_link('clicks',$row->{messID},$row->{linkID});
		$ouput.=<<ALL__;
		<TR class=data1>
			<TD>&nbsp;</TD>
			<TD>$row->{linkname} <a href="$row->{url}" target="_blank">$row->{url}</a></TD>
			<TD align=right>$row->{prospects}<a href="$l_p" title="$LNG{LINKS_VIEW_CLICKS}">...</a></TD>
			<TD align=right>$row->{clicks}<a href="$l_c" title="$LNG{LINKS_VIEW_PROSP}">...</a></TD>
		</TR>
ALL__
		$totalClicks+=$row->{clicks};
		$mess{$row->{messID}}[0]+=$row->{clicks};
	}	
	map{$ouput=~s/###CL$_#/$mess{$_}[0]/}keys %mess;
	 my $sql=<<ALL__;
SELECT 
	fk_mess AS messID, 
	COUNT( DISTINCT fk_user ) AS prospects
FROM `${PREF}link_clicks` 
LEFT JOIN ${PREF}mess ON pk_mess = fk_mess
WHERE ${PREF}mess.fk_account=? $where
GROUP BY ${PREF}mess.fk_account
ALL__
	my $total=select_one_db($sql,$PAR{account});
	my $l_p=get_links_stat_link('prospects',undef,undef);
	my $l_c=get_links_stat_link('clicks',undef,undef);
	$ouput.=<<ALL__;
		<TR class=dataheader>
				<TD colspan=2 align=right><B>$LNG{STAT_TOTAL}:</B></TD>
				<TD align=right><B><u>$total->{prospects}</u><a href="$l_p" title="$LNG{LINKS_VIEW_PROSP}">...</a></B></TD>
				<TD align=right><B><u>$totalClicks</u><a href="$l_c" title="$LNG{LINKS_VIEW_CLICKS}">...</a></B></TD>
		</TR>	
	</table>
ALL__
	$page->add_regesp('{report}',$ouput);
	$page->ParseData;
	return $page->as_string;	
}
sub get_links_stat_link{
	my %p=%PAR;
	$p{modelog}=shift;
	$p{'message'}=shift;
	$p{'link'}=shift;
	my $email=shift;
	$p{emailsearch} = $email if $email;
	return "$SCRIPT_NAME?".join("&",map{"$_=$p{$_}"}keys%p);

}
sub print_links{
	if ($PAR{modelog} eq 'mess'){
		return &print_links_mess;
	}elsif($PAR{modelog} eq 'prospects'){
		return &print_links_mesrospects(1);
	}elsif($PAR{modelog} eq 'clicks'){
		return &print_links_mesrospects(0);
	}
	
	my $page=new repparser (
		DATA=>$links_shabl,
		FROM=>'#start#links',TO=>'#end#links'
	);
	if($PAR{'act3'} eq 'clean' && $PAR{id}){
		$db->do("DELETE FROM ${PREF}link_clicks WHERE fk_link=?",undef,$PAR{id}); &Error("Deleting links clicks");			
		OPTIMIZEtables();
		print $q->redirect("$SCRIPT_NAME?act=$PAR{act}&account=$PAR{account}&act2=$PAR{act2}&ses=$PAR{ses}");
		exit;
	}
	if($PAR{'delete'}){
		my @ID=$q->param('id');
		if(@ID){
			@ID=map{$db->quote($_)}@ID;
			my $in=join(" , ",@ID);
			$db->do("DELETE FROM ${PREF}links WHERE pk_link IN ($in)"); &Error("Deleting links");
			$db->do("DELETE FROM ${PREF}link_clicks WHERE fk_link IN ($in)"); &Error("Deleting links clicks");			
			OPTIMIZEtables();
		}
		print $q->redirect("$SCRIPT_NAME?act=$PAR{act}&account=$PAR{account}&act2=$PAR{act2}&ses=$PAR{ses}");
		exit;	
	}
	my $sql="SELECT * FROM ${PREF}links  WHERE fk_account=? ORDER BY pk_link";
	my $out=$db->prepare($sql);
	$out->execute($PAR{account});
	&Error($sql);
	my $all_count=0;
	while (my $output=$out->fetchrow_hashref){
		my $c=select_one_db("SELECT count(pk_link_click) AS count FROM ${PREF}link_clicks WHERE fk_link=?",$output->{pk_link}); 
		my $count=$c->{count} || 0;
		$all_count+=$count;
		my $u=select_one_db("SELECT count(DISTINCT fk_user) AS count FROM ${PREF}link_clicks WHERE fk_link=?",$output->{pk_link}); 
		my $u_count=$u->{count} || 0;
		my $l="<a href=\"$SCRIPT_NAME?act=$PAR{act}&account=$PAR{account}&act2=changelink&ses=$PAR{ses}&id=$output->{pk_link}\" title=\"$LNG{LINKS_CHANGE_LINK} $output->{name}\">$LNG{LINKS_CHANGE}</a>";
		my $l_cl='&nbsp;';
		$l_cl=qq|<a onClick="return confirm('Are you sure you want to delete all statistics on selected link?');" href="$SCRIPT_NAME?act=$PAR{act}&account=$PAR{account}&act2=links&act3=clean&ses=$PAR{ses}&id=$output->{pk_link}" title="Clean all statistics on link $output->{name}" >$LNG{LINK_CLEAN}</a>| if $count;
		$page->AddRow({
				id=>$output->{pk_link},
				name=>$output->{name},
				url=>$output->{redirect_link},
				clicks=>$count,
				users=>$u_count,
				'link'=>$l,
				clean=>$l_cl
			});
		
	}
	my $u=select_one_db("SELECT count(DISTINCT fk_user) AS count FROM ${PREF}link_clicks LEFT JOIN ${PREF}links ON pk_link=fk_link WHERE fk_account=? GROUP BY fk_user",$PAR{account}); 
	my $u_count=$u->{count} || 0;
	$page->add_regesp('{users}',$u_count);
	$page->add_regesp('{clicks}',$all_count);
	$page->ParseData;
	return $page->as_string;	
}

#######################
sub print_account_page{
	my %map;
	%map=(	""       =>\&print_main_account_data,
		columns  =>\&print_columns,
		mess     =>\&print_account_mess,
		newmess  =>\&print_account_newmess,
		users_new    =>\&print_users_new,
		fieldform=>\&print_field_form,
		delfield =>\&delete_field,
		up       =>\&move_up_field,
		down     =>\&move_down_field,
		config   =>\&print_config,
		#rss   =>\&print_config_rss,
		links   =>\&print_links,
		changelink   =>\&print_changelink
	);
	
	$main_page=new dparser(
		DATA=>"$SHABL_DIR/main-shabl.html"
	);
	#$main_page->add_regesp('{account_name}',$q->a({href=>get_full_url({act2=>""})},$ACCOUNT{$PAR{account}}));
	if($PAR{act2} eq 'newmess'){
		if($CONF{HTMLEditorDisable}){
			$main_page->add_regesp('bodyonload','');
		}else{
			$main_page->add_regesp('bodyonload',' onload="areaedit_init()"');
		}
		
	}else{
		$main_page->add_regesp('bodyonload','');
	}
	$main_page->add_regesp('{account_name}',
		"<A href=$ENV{SCRIPT_NAME}?ses=$PAR{ses}&account=$PAR{account}&act=mainbody>$ACCOUNT{$PAR{account}}</A>"
	);
	$main_page->add_regesp('{account_nm}',"$ACCOUNT{$PAR{account}}");
	my $meta = <<ALL__;
	<meta http-equiv="Content-Type" content="text/html; charset=$CONF{defcharset}">
ALL__
	$meta="" unless $CONF{defcharset};
	$main_page->add_regesp('{__META__}',$meta);
	$main_page->add_regesp('{account}',$PAR{account});
	#$main_page->add_regesp('{main_menu}',get_account_menu(\@ACCOUNTMENU));
	$main_page->add_regesp('{main_menu}',
		get_hor_menu(\@ACCOUNTMENU,{ses=>$PAR{ses},act=>$PAR{act},act2=>$PAR{act2},account=>$PAR{account}},[['menu','menuACT'],['menu2','menu2ACT'],['menu3','menu3ACT']]));
	#$main_page->add_regesp('{main_menu_body}',get_full_menu(\@ACCOUNTMENU));
	my $func_ref;
	if ($map{$PAR{act2}}) {
		$func_ref=$map{$PAR{act2}};
	}else{
		$func_ref=sub{return $q->h1($LNG{ERROR_NOT_CHANGE_URL})}
	}
	$main_page->add_regesp('{body}',&$func_ref);
	$main_page->ParseData;
	&printheader;
	$main_page->print;	
}
####################
sub print_main{
	unless(exists($ACCOUNT{$PAR{account}})){
		if($PAR{shownews}){
			print $q->redirect("http://fump.biz");
		}elsif($CONF{splashsettings} eq 'daily_stats'){
			print $q->redirect("$ME?ses=$PAR{ses}&act=statdaily");
		}elsif($CONF{splashsettings} eq 'activity'){
			print $q->redirect("$ME?ses=$PAR{ses}&act=stat&act2=log");
		}elsif($CONF{splashsettings} eq 'curbroadcast'){
			print $q->redirect("$ME?ses=$PAR{ses}&act=stat&act2=curlog");
		}elsif($CONF{splashsettings} eq 'totalstat'){
			print $q->redirect("$ME?ses=$PAR{ses}&act=stat&act2=total");
		}elsif($CONF{splashsettings} eq 'bounced'){
			print $q->redirect("bounce.cgi?ses=$PAR{ses}&act=messages");
		}elsif($CONF{splashsettings} eq 'bounced_total'){			
			print $q->redirect("bounce.cgi?ses=$PAR{ses}&act=totals");
		}else{
			if($CONF{splashsettings}=~/^account_(\d+)/ and exists($ACCOUNT{$1})){
				print $q->redirect("$ME?ses=$PAR{ses}&act=mainbody&account=$1");
			}else{
				print $q->redirect("http://fump.biz/");
			}
		}
		exit;
	}else{	
		&print_account_page;
	}

}
#########################
###accounts
sub DublicateAccountTable{
	my $table=shift;
	my $old_account=shift;
	my $new_account=shift;
	my $p_key=shift;
	my $f_key=shift;
	my $h_where=shift;
	my @where=@{$h_where};
	push @where,"$f_key=?";
	my $WHERE;
	$WHERE="WHERE ".join(" AND ",@where) if @where;
	my $sql="SELECT * FROM $table $WHERE ";
	my $out=$db->prepare($sql);
	$out->execute($old_account);
	&Error($sql);
	while (my %output=%{$out->fetchrow_hashref}){
		delete($output{$p_key});
		$output{$f_key}=$new_account;
		insert_db("$table",\%output);
	}
}

######################
sub DeleteAccount{
	my $key=shift;
	return unless $key;
	my @keys=();
	push(@keys,$key);
	my $accounts="(".join(",",@keys).")";
	$db->do("DELETE FROM ${PREF}account WHERE pk_account in $accounts");
	&Error("DELETE FROM ${PREF}account WHERE pk_account in $accounts");
	$db->do("DELETE FROM ${PREF}user WHERE fk_account in $accounts");	&Error("DELETE FROM ${PREF}user WHERE fk_account in $accounts");
	my $ary_ref = $db->selectcol_arrayref("select pk_mess from ${PREF}mess WHERE fk_account in $accounts");	&Error("select pk_mess from ${PREF}mess WHERE fk_account in $accounts");
	$db->do("DELETE FROM ${PREF}attach WHERE fk_mess in (".join(",",@{$ary_ref}).")") if @{$ary_ref};
	$db->do("DELETE FROM ${PREF}tosend WHERE fk_mess in $accounts");	&Error("DELETE FROM ${PREF}tosend WHERE fk_mess in $accounts");
	$db->do("DELETE FROM ${PREF}mess WHERE fk_account in $accounts");	&Error("DELETE FROM ${PREF}mess WHERE fk_account in $accounts");
	$db->do("DELETE FROM ${PREF}conf WHERE fk_account in $accounts");	&Error("DELETE FROM ${PREF}conf WHERE fk_account in $accounts");
	my $ary_ref = $db->selectcol_arrayref("select pk_fields from ${PREF}fields WHERE fk_account in $accounts");	&Error;
	$db->do("DELETE FROM ${PREF}doppar WHERE fk_fields in (".join(",",@{$ary_ref}).")") if @{$ary_ref};
	&Error("DELETE FROM ${PREF}doppar WHERE fk_fields in (".join(",",@{$ary_ref}).")");
	my $ary_ref = $db->selectcol_arrayref("select pk_link from ${PREF}links WHERE fk_account in $accounts");	&Error;
	$db->do("DELETE FROM ${PREF}link_clicks WHERE fk_link in (".join(",",@{$ary_ref}).")") if @{$ary_ref};
	&Error("DELETE FROM ${PREF}link_clicks WHERE fk_link in (".join(",",@{$ary_ref}).")");
	$db->do("DELETE FROM ${PREF}links WHERE fk_account in $accounts");
	&Error("DELETE FROM ${PREF}links WHERE fk_account in $accounts");
	OPTIMIZEtables();
}
###################
sub OPTIMIZEtables{	
	foreach(@backup_tables){
		$db->do("OPTIMIZE TABLE ${PREF}$_");
		&Error;
	}
}
######################
sub InverseStatusAccounts{
	return unless $q->param('reckey');
	my @keys=$q->param('reckey');
	foreach my $key(@keys){
		$db->do("UPDATE  ${PREF}account SET isact=IF(isact=0,1,0) WHERE pk_account=$key");
		&Error;
	}
	print $q->redirect("$SCRIPT_NAME?ses=$PAR{ses}&act=account");
	exit(1);
}
####################
sub print_account{
	&printheader;
	my $page=new repparser
	DATA=>"$SHABL_DIR/accounts.html";
	local $OUT;
	$page->Hide("<!--HIDE_IF_NOT_XML_IMPORT-->") unless(-f "xmlimport.cgi");
	$page->Hide("<!--HIDE_IF_NOT_XML_EXPORT-->") unless(-f "xmlexport.cgi");
	&check_for_holes($page,'{ATTANTION}');
	my $sql="SELECT * from ${PREF}account ORDER by position asc , name asc";
	my $out=$db->prepare($sql);
	$out->execute();	
	while (my $output=$out->fetchrow_hashref){
		$output->{img} = "content.cgi?get=image&mode=gif&f=";
		$output->{img}.=$output->{isact}?'active':'inact';
		$output->{status}=$output->{isact}?$LNG{MESS_ACTIVE}:$LNG{MESS_INACTIVE};
		$page->AddRow($output);
	}
	$page->ParseData;
	$page->print;
}
####################
sub show_account_browser{
	my $sql="SELECT * from ${PREF}account ORDER by name asc";
	my $out1=$db->prepare($sql);
	$out1->execute();
	if($out1->rows<1){
		return "<H2>$LNG{ACCOUNT_NO_ACCOUNTS}</H2>" ;
	}
	#return "Shet i'm here";	
	my $OUT=<<ALL__;
	
<table width="100%" border="0" cellspacing="0" cellpadding="0">	
<TR><TD class="line">
<table width="100%" border="0" cellspacing="1" cellpadding="2">
    <tr class="dataheader">
      <td width="94%" colspan="2">$LNG{ACCOUNT_YOUR_ACCOUNTS}:</td>
    </tr>
ALL__

	while (my %output=%{$out1->fetchrow_hashref}){
		my $status;
		$status=" ($LNG{ACCOUNT_DISABLED})" if ($output{isact}==0);
		
		$OUT.=<<ALL__;
	    <tr class="data">
		      <td width="3%"><input type="checkbox" name="reckey" value="$output{pk_account}"></td>
		      <td width="94%"><NOBR><a href="$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody&account=$output{pk_account}" target="main">$output{name}</a>$status</NOBR></td>
	    </tr>
ALL__
	}

	$OUT.=<<ALL__;
	<tr class="data">
	 <td colspan="2" align="center">
	  <input type="submit" value="$LNG{DEL_SELECTED}" class="buttonmy" name="bn_delete"
	   onClick="if (confirm('$LNG{ACCOUNT_DELETE_QUESTION}')==true){ goToURL('parent.frames[\\'main\\']', '$SCRIPT_NAME?ses=$PAR{ses}&act=mainbody') } else {return(false);}">	
	 </td>
	</tr>
	<tr class="data">
	<td colspan="2" align="center">
	<input type="submit" value="$LNG{ACCOUNT_INVERT_STATUS}" class="buttonmy" name="bn_inverse">
	</td></tr>
</table>
</td></tr></table>
<BR><BR>
ALL__
return	$OUT;
}
sub check_for_holes{
	my ($page,$regesp)=@_;
	my @files=();
	my @files=<up*.cgi>;
	push(@files, 'install.cgi' ) if -f 'install.cgi';
	if (@files){
		my @badfileslist=map{"<LI><STRONG>$_</STRONG>\n"}@files;
		$page->add_regesp($regesp,$LNG{ATTANTIONFILES1}.join(" ",@badfileslist).$LNG{ATTANTIONFILES2});
	}else{
		$page->add_regesp($regesp,"");
	}
}
####################
#end accounts
####################
sub print_frameset{
	&printheader;
	my $page=new dparser
	DATA=>"$SHABL_DIR/mainframe.html"
	;
	$page->ParseData;
	$page->print;
}
#####################
#end mapping functions
#####################
sub openXinha{
	&printheader;
	my $page=new hfparser
	DATA=>"$SHABL_DIR/xinha.html"
	;
	$page->set_input("messhtml2", {columns=>70,rows=>20,id=>"messhtml2",
		ONSELECT=>"storeCaret(this);",
		ONCLICK=>"storeCaret(this);",
		ONKEYUP=>"storeCaret(this);"});	
	my $htmleditor_script;
	open(F,'shabl/htmlarea.js') or die "Can not open file shabl/htmlarea.js please check did this file exists in shabl folder";
	while(<F>){
		s/\{HTMLEditorURL\}/$HTMLEditorURL/s;
		$htmleditor_script.=$_;
	}
	$page->add_regesp('{personal_links_html}',&print_personalize_links(3));
	$page->add_regesp('{HTMLEDITORSCRIPT}',$htmleditor_script);
	$page->ParseData;
	$page->print;
}
sub print_statdaily{
	&printheader;
	print GetStatDailyPage();
	exit;
}
sub print_logout{
	$db->do("DELETE FROM ${PREF}ses where ran=?",undef,$PAR{ses});
	&Error;
	print $q->redirect($SCRIPT_NAME);
	exit;

}
