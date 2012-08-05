#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01.05                                                    #
# Last modified 19/07/2010                                           #
######################################################################
use lib('lib');
require 'conf.cgi';
&par_prepare;
$shabl_page_install="$SHABL_DIR/install.html";
local %func;
local @tables=sort {$a cmp $b} qw(account attach conf doi doiaccounts doppar fields log mess ses tosend user);
%func=(1=>1,2=>1,3=>1,4=>1);
if($PAR{showpath}){
print_show_path();
}
&print_all;
sub print_show_path{
print $q->header;
	print $q->start_html("Startercron installation helper");
	print "<H1 align=center>Startercron installation helper</H1>";
	print qq|<H2 align=center><a href="$ENV{SCRIPT_NAME}?showpath=1&isupd=1">Click here to update your startercron file on server</A></H1>|;
	
	#map{print "$_ = $ENV{$_}<BR>\n"}keys %ENV;
	unless(-f 'broadcaster'){
		print "<H1> <FONT color=red>This is not your FUMP directory: I can not find the broadcaster script</FONT></H1>";
		exit;
	}
	my $Perl_path=$^X;
	my $maillist_dir;
	if (length($ENV{SCRIPT_FILENAME})){
		$maillist_dir=$ENV{SCRIPT_FILENAME};
	}else{
		$maillist_dir=$ENV{DOCUMENT_ROOT}.$ENV{SCRIPT_NAME};
	}
	$maillist_dir=~s/install\.cgi//;
	print $q->p("");
	if($PAR{isupd}){
		my $cronfile="${maillist_dir}cron/startercron";
		open(FILE,">$cronfile") || die "Can not open file  $cronfile for writing: $!";
		print FILE <<ALL__;
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01.04                                                    #
# Last modified 09/01/2009                                           #
######################################################################
#Put here absolute to your broadcaster directory 
\$yourdir='$maillist_dir';
#You can  run this script from cron like
#*/15 * * * *  $Perl_path ${maillist_dir}cron/startercron
#in this case script will starts each 15 minutes
chdir(\$yourdir) || die "Can not change dir to \$yourdir : \$!";	
exec('$Perl_path broadcaster');
ALL__
		close(FILE);
		print "<H1 align=center><FONT color=red>Startercron updated</font></H1>";
	}
	print <<ALL__;
<P>Your maillist absolute path is <B>$maillist_dir</B>
<P>So you need to modify startercron file to
<P>Your perl executible is $Perl_path
<HR>
<PRE>
#Put here absolute to your broadcaster directory 
\$yourdir='<B>$maillist_dir</B>';
#You can  run this script from cron like
#*/15 * * * *  $Perl_path ${maillist_dir}cron/startercron
#in this case script will starts each 15 minutes
chdir(\$yourdir) || die "Can not change dir to \$yourdir : \$!";	
exec('$Perl_path broadcaster'); 
</PRE>
<HR>
ALL__
exit;
}

sub print_all{
	&printheader;
	$PAR{step}=1 unless $PAR{step};
	my $page=new hfparser(
		DATA=>$shabl_page_install
	);
	$page->SplitData("<!--START-->","<!--END-->");
	my $what;
	$what = &print_step1 if exists $func{$PAR{step}};
	$what = "<h1 class=\"mess\">Do not change the URL</h1>" unless exists $func{$PAR{step}};
	$page->replaceINSIDE($what);
	$page->ParseData;
	$page->print;
}
sub print_step1{
	my $page=new hfparser(
		DATA=>$shabl_page_install,
		#ERROR_AFTER_INPUT=>0
	);
	if ($PAR{step}>1){
		if ($PAR{step}==2){
			unless($PAR{prefix}){
				$page->set_error("prefix","Database prefix is required");
			}else{
				unless ($PAR{prefix}=~/^[a-z][a-z_0-9]{0,8}$/){
					$page->set_error("prefix","Database prefix is incorrect it must be 1-8 chars a-z or '_'");					
				}

			}
			unless($page->is_error){
				unless($db = DBI->connect("DBI:mysql:database=$PAR{db};host=$PAR{host}",$PAR{user},$PAR{password})){
					#$page->set_error("GLOBAL","Not connected to database $PAR{db}: <BR> Error: $DBI::err : $DBI::errstr ");
					$page->set_error("host"," ");
					$page->set_error("db","Not connected to database $PAR{db}: <BR> Error: $DBI::err : $DBI::errstr ");
					$page->set_error("user"," ");
					$page->set_error("password"," ");				
				}
			}
			
			unless($page->is_error){
				my $out;
				$out="_us:$PAR{user};_db:$PAR{db};_pass:$PAR{password};_pref:$PAR{prefix};_host:$PAR{host}";
				open (OUT,">$c_file") || die "Can not write to file $c_file - $!";
				print OUT fs($out,$cfg_psd x ceil(length($out)/length($cfg_psd)));
				close(OUT);
				&db_prepare;
				return &print_step2;
			}
		}else{
			&db_prepare;
			return &print_step2;
		}
	}
	$page->SplitData("<!--START1-->","<!--END1-->");
	$page->deleteBEFORE_AFTER();
	$page->set_def("host","localhost");
	$page->set_def("prefix","swd_");
	$page->set_input("prefix",{maxlength=>8,size=>8});
	$page->ParseData;
	return $page->as_string;
}
sub get_tables{
	my $rows;
	my %tables;
	map{$tables{$_}=1}@{$db->selectcol_arrayref("SHOW TABLES LIKE '%'")};
	
	foreach $table(@backup_tables){
		my $status='clean';
		if (exists($tables{"$PREF$table"})){
			$isexists=1;
			$status="<FONT color=red>EXISTS!</FONT>" 			
		}
$rows.=<<ALL__;
<tr class="data"> 
   <td align="left" width="50%">$PREF$table</td>
   <td align="center" width="50%">$status</td>
</tr>
ALL__
	}
	return $rows;
}
########################
sub print_step2{
	my $page=new hfparser(
		DATA=>$shabl_page_install,
	);
	if ($PAR{step}>2){
		if ($PAR{step}==3){
			if ($PAR{install}){
				my $query;
				while(<DATA>){
					next if /^#/;
					$query.=$_;
				}
				$query=~s/swd_/$PREF/g;
				multiSQL($query);
				#Update FUMP
				@UPDATE=LoadUpdateStructure();
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
							push (@UPG, $_);
						}
						
					}
				}@UPDATE;
				#END UPDATE
			}
			return &print_step3;
		}else{
			return &print_step3;
		}
	}
	local $isexists=0;
	$page->add_regesp("{tables}",&get_tables);
	$page->add_regesp("{DATA}",$DATABASE);
	$page->SplitData("<!--START2-->","<!--END2-->");
	$page->deleteBEFORE_AFTER();
	unless ($isexists){
		$page->SplitData("<!--HIDE-->","<!--ENDHIDE-->");
		$page->replaceINSIDE(undef);	
	}
	$page->ParseData;
	return $page->as_string;
}
########################
sub print_step3{
	my $page=new hfparser(
		DATA=>$shabl_page_install,
	);
	if ($PAR{step}>3){
		if ($PAR{step}==4){
			if ($PAR{newpass1} && $PAR{newpass2}){
				$page->set_error("newpass1","Not equal") if ($PAR{newpass1} ne $PAR{newpass2});
				$page->set_error("newpass2","Not equal") if ($PAR{newpass1} ne $PAR{newpass2});
			}else{
				$page->set_error("newpass1","Required") unless defined $PAR{newpass1};
				$page->set_error("newpass2","Required") unless defined $PAR{newpass2};			
			}
			unless($page->is_error){
				save_config(0,"adminpwd",$PAR{newpass1});
				return &print_step4;
			}
		}else{
			return &print_step4;
		}
	}
	$page->SplitData("<!--START3-->","<!--END3-->");
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
##################
sub print_step4{
	my $page=new hfparser(
		DATA=>$shabl_page_install,
	);
	$page->SplitData("<!--START4-->","<!--END4-->");
	$page->deleteBEFORE_AFTER();
	$page->ParseData;
	return $page->as_string;
}
__DATA__
# Database : `fump418`

# Table structure for table `swd_account`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:11 PM
#

DROP TABLE IF EXISTS `swd_account`;
CREATE TABLE `swd_account` (
  `pk_account` int(11) default NULL auto_increment,
  `name` varchar(30) NOT NULL ,
  `isact` tinyint(4) NOT NULL default '1',
  PRIMARY KEY (`pk_account`)
) TYPE=MyISAM AUTO_INCREMENT=2 ;

#
# Dumping data for table `swd_account`
#

INSERT INTO `swd_account` VALUES (1, 'sample', 0);

# --------------------------------------------------------

#
# Table structure for table `swd_attach`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_attach`;
CREATE TABLE `swd_attach` (
  `pk_attach` int(11) default NULL auto_increment,
  `filename` varchar(80) NOT NULL default '',
  `data` longblob NOT NULL,
  `fk_mess` int(11) NOT NULL default '0',
  `len` int(11) NOT NULL default '0',
  PRIMARY KEY (`pk_attach`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

#
# Dumping data for table `swd_attach`
#


# --------------------------------------------------------

#
# Table structure for table `swd_brodcastlog`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_brodcastlog`;
CREATE TABLE `swd_brodcastlog` (
  `pk_broadcastlog` int(11) default NULL auto_increment,
  `date` timestamp(14) ,
  `procnomber` tinyint(4) NOT NULL default '0',
  `pid` varchar(6) NOT NULL default '',
  `log` text NOT NULL,
  PRIMARY KEY (`pk_broadcastlog`),
  KEY `procnomber`(`procnomber`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

#
# Dumping data for table `swd_brodcastlog`
#


# --------------------------------------------------------

#
# Table structure for table `swd_conf`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:11 PM
#

DROP TABLE IF EXISTS `swd_conf`;
CREATE TABLE `swd_conf` (
  `pk_conf` varchar(30) NOT NULL default '',
  `conf_value` text NULL,
  `discr` text,
  `fk_account` int(11) NOT NULL default '0',
  KEY `pk_conf`(`pk_conf`),
  PRIMARY KEY (`pk_conf`,`fk_account`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_conf`
#

INSERT INTO `swd_conf` VALUES ('VERSION', '5.1',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('defname', 'Friend',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('subscribeemail', 'subscribe@domain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('pop3server', 'pop3.yourdomain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('pop3user', 'johndoe',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('pop3pass', '12345',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('pop3port', '110',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('fromname', 'Your Name',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('fromemail', 'noreply@yourdomain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('isaddunsubscrlink', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('isnotifsubscr', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('isnotifunsubscr', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('isdoi', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('doiconfurl', 'http://www.yourdomain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('ispop3', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('redirsub', 'http://www.yourdomain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('redirrem', 'http://www.yourdomain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('PID', '0',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('timebroadcast', '1053972878',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('sendmail', '/usr/sbin/sendmail',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('modsend', 'sendmail',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('smtp', 'localhost',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('adminname', 'Admin',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('adminemail', 'yourname@yourdomain.com',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('statbyemail', 'on',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('enablelog', 'on',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('sendsubscr', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('sendunsubscr', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('maxlim', '23',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('timecorr', '+00:00',  NULL, 0);
INSERT INTO `swd_conf` VALUES ('replyto', 'noreply@yourdomain.com',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('uppercase', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('messlogging', 'on',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('ispurge', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('banmails', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('banmailserror', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('defcharset', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('no_uppercase', '',  NULL, 1);
INSERT INTO `swd_conf` VALUES ('adminpwd', '',  NULL, 0);

# --------------------------------------------------------

#
# Table structure for table `swd_doi`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_doi`;
CREATE TABLE `swd_doi` (
  `pk_doi` int(11) default NULL auto_increment,
  `ran` char(10) NOT NULL default '',
  PRIMARY KEY (`pk_doi`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

#
# Dumping data for table `swd_doi`
#


# --------------------------------------------------------

#
# Table structure for table `swd_doiaccounts`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_doiaccounts`;
CREATE TABLE `swd_doiaccounts` (
  `fk_doi` int(11) NOT NULL default '0',
  `fk_account` int(11) NOT NULL default '0',
  `fk_user` int(11) NOT NULL default '0',
  PRIMARY KEY (`fk_doi`,`fk_account`),
  KEY `fk_user`(`fk_user`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_doiaccounts`
#


# --------------------------------------------------------

#
# Table structure for table `swd_doppar`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_doppar`;
CREATE TABLE `swd_doppar` (
  `fk_fields` int(11) NOT NULL default '0',
  `fk_user` int(11) NOT NULL default '0',
  `value` text,
  PRIMARY KEY (`fk_fields`,`fk_user`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_doppar`
#


# --------------------------------------------------------

#
# Table structure for table `swd_fields`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:11 PM
#

DROP TABLE IF EXISTS `swd_fields`;
CREATE TABLE `swd_fields` (
  `pk_fields` int(11) default NULL auto_increment,
  `fieldname` varchar(40) NOT NULL default '',
  `fk_account` int(11) NOT NULL default '0',
  `is_req` int(11) NOT NULL default '0',
  `rang` tinyint(4) NOT NULL default '1',
  `type` enum('text','textarea') NOT NULL default 'text',
  PRIMARY KEY (`pk_fields`),
  KEY `fieldaddr`(`fieldname`,`fk_account`,`pk_fields`)
) TYPE=MyISAM AUTO_INCREMENT=16 ;

#
# Dumping data for table `swd_fields`
#

INSERT INTO `swd_fields` VALUES (7, 'Date', 1, 0, 4, 'text');
INSERT INTO `swd_fields` VALUES (6, 'City', 1, 0, 3, 'text');
INSERT INTO `swd_fields` VALUES (5, 'Address', 1, 0, 2, 'text');
INSERT INTO `swd_fields` VALUES (8, 'Date2', 1, 0, 5, 'text');
INSERT INTO `swd_fields` VALUES (9, 'sex', 1, 0, 6, 'text');
INSERT INTO `swd_fields` VALUES (10, 'sname', 1, 0, 7, 'text');
INSERT INTO `swd_fields` VALUES (11, 'state', 1, 0, 8, 'text');
INSERT INTO `swd_fields` VALUES (12, 'url1', 1, 0, 9, 'text');
INSERT INTO `swd_fields` VALUES (13, 'url2', 1, 0, 10, 'text');
INSERT INTO `swd_fields` VALUES (14, 'Zip', 1, 0, 11, 'text');
INSERT INTO `swd_fields` VALUES (15, 'Country', 1, 0, 1, 'text');

# --------------------------------------------------------

#
# Table structure for table `swd_link_clicks`
#
# Creation: Dec 04, 2004 at 07:09 PM
# Last update: Dec 04, 2004 at 07:09 PM
#

DROP TABLE IF EXISTS `swd_link_clicks`;
CREATE TABLE `swd_link_clicks` (
  `pk_link_click` int(11) default NULL auto_increment,
  `fk_link` int(11) default '0',
  `fk_user` int(11) default '0',
  `fk_mess` int(11) default '0',
  `timestamp` timestamp(14) ,
  PRIMARY KEY (`pk_link_click`),
  KEY `fk_account`(`fk_user`,`fk_mess`,`fk_link`),
  KEY `timestamp`(`timestamp`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

#
# Dumping data for table `swd_link_clicks`
#


# --------------------------------------------------------

#
# Table structure for table `swd_links`
#
# Creation: Dec 04, 2004 at 07:09 PM
# Last update: Dec 04, 2004 at 07:09 PM
# patch 001 changed redirect_link from varchar to text type
#

DROP TABLE IF EXISTS `swd_links`;
CREATE TABLE `swd_links` (
  `pk_link` int(11) default NULL auto_increment,
  `name` varchar(100) NOT NULL default '',
  `redirect_link` TEXT NOT NULL default '',
  `fk_account` int(11) NOT NULL default '0',
  PRIMARY KEY (`pk_link`),
  KEY `fk_account`(`fk_account`)
) TYPE=MyISAM AUTO_INCREMENT=3 ;

#
# Dumping data for table `swd_links`
#

INSERT INTO `swd_links` VALUES (1, 'Test1', 'http://www.yahoo.com', 1);
INSERT INTO `swd_links` VALUES (2, 'Test 2', 'http://www.microsoft.com', 1);

# --------------------------------------------------------

#
# Table structure for table `swd_log`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_log`;
CREATE TABLE `swd_log` (
  `pk_log` int(11) default NULL auto_increment,
  `date` datetime NOT NULL default '0000-00-00 00:00:00',
  `log` text,
  PRIMARY KEY (`pk_log`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

#
# Dumping data for table `swd_log`
#


# --------------------------------------------------------

#
# Table structure for table `swd_mess`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:11 PM
#

DROP TABLE IF EXISTS `swd_mess`;
CREATE TABLE `swd_mess` (
  `pk_mess` int(11) default NULL auto_increment,
  `fk_account` int(11) NOT NULL default '0',
  `subject` varchar(100) NOT NULL default '',
  `mess` text NULL,
  `type` enum('text','html') NOT NULL default 'text',
  `typesend` enum('manual','doi','auto','senddat','subscribe','unsubscribe') NOT NULL default 'manual',
  `days` int(11) default NULL,
  `senddat` date default NULL,
  `sent` int(11) default '0',
  `datesend` timestamp(14) ,
  `priority` int(11) default NULL,
  `encoding` varchar(15) default NULL,
  `issendnow` tinyint(4) NOT NULL default '0',
  PRIMARY KEY (`pk_mess`),
  KEY `typesend`(`typesend`)
) TYPE=MyISAM AUTO_INCREMENT=6 ;

#
# Dumping data for table `swd_mess`
#

INSERT INTO `swd_mess` VALUES (2, 1, 'Test sequential message for [FULLNAME]', '[FULLNAME] will extract and print your prospect\'s whole name (i.e. \'Mr. [FULLNAME],\' will print \'Mr. John Doe\', if your prospect\'s name is John Doe). \r\n[EMAIL] will extract and print your prospect\'s e-mail address (i.e. \'Your e-mail address is [EMAIL]\' will output \'Your e-mail address is john@domain.com\', if your prospect\'s e-mail address is john@domain.com. \r\n[DATE] will print current date in dd/mm/yyyy format. \r\n[DATE+32d] [DATE-32d] [DATE+1m] [DATE-1m] [DATE+1y] [DATE-1y] will print corrected current date in dd/mm/yyyy format. \r\nExtra merge field words\r\n[ADD15] - Country \r\n[ADD5] - Address \r\n[ADD6] - City \r\n[ADD7] - Date \r\n[ADD8] - Date2 \r\n[ADD9] - sex \r\n[ADD10] - sname \r\n[ADD11] - state \r\n[ADD12] - url1 \r\n[ADD13] - url2 \r\n[ADD14] - Zip\r\n', 'text', 'auto', 1,  NULL, 0, 20030607165021,  NULL,  NULL, 0);
INSERT INTO `swd_mess` VALUES (5, 1, 'Sample manual message  for [FULLNAME]', 'This is the Sample manual message  for [FULLNAME]', 'text', 'manual', 0,  NULL, 0, 20030607165002,  NULL,  NULL, 0);
INSERT INTO `swd_mess` VALUES (3, 1, 'Subscribe message', 'Put your subscribe message here', 'text', 'subscribe', 0,  NULL, 0, 20030211215818,  NULL,  NULL, 0);
INSERT INTO `swd_mess` VALUES (4, 1, 'Unsubscribe message', 'Your message', 'text', 'unsubscribe', 0,  NULL, 0, 20021202234251,  NULL,  NULL, 0);
INSERT INTO `swd_mess` VALUES (1, 1, 'Please confirm your subscription', 'To confirm your subscription, click on the link below \r\n(you must be connected to the internet at the time):\r\n\r\n[CONFIRM_URL]\r\n\r\nIf you did not make the request, there is no need\r\nto take any further action.\r\n', 'text', 'doi', 0,  NULL, 0, 20030607164945, 2,  NULL, 0);

# --------------------------------------------------------

#
# Table structure for table `swd_process_loc`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_process_loc`;
CREATE TABLE `swd_process_loc` (
  `pk_process_loc` int(11) default NULL auto_increment,
  `date` datetime NOT NULL default '0000-00-00 00:00:00',
  `PID` varchar(8) NOT NULL default '',
  `procnomber` tinyint(4) NOT NULL default '0',
  PRIMARY KEY (`pk_process_loc`),
  KEY `procnomber`(`procnomber`)
) TYPE=MyISAM AUTO_INCREMENT=1 ;

#
# Dumping data for table `swd_process_loc`
#


# --------------------------------------------------------

#
# Table structure for table `swd_sentlog`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_sentlog`;
CREATE TABLE `swd_sentlog` (
  `fk_user` int(11) NOT NULL default '0',
  `fk_mess` int(11) NOT NULL default '0',
  `date` datetime default NULL,
  PRIMARY KEY (`fk_user`,`fk_mess`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_sentlog`
#


# --------------------------------------------------------

#
# Table structure for table `swd_ses`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 07, 2004 at 11:38 AM
# Last check: Dec 07, 2004 at 11:38 AM
#

DROP TABLE IF EXISTS `swd_ses`;
CREATE TABLE `swd_ses` (
  `pk_ses` int(11) default NULL auto_increment,
  `ran` varchar(25) NOT NULL default '0',
  `date` datetime default NULL,
  `host` varchar(14) NOT NULL default '',
  PRIMARY KEY (`pk_ses`)
) TYPE=MyISAM AUTO_INCREMENT=5 ;

#
# Dumping data for table `swd_ses`
#

INSERT INTO `swd_ses` VALUES (4, 'ihSBifrvFXEGfX5c0oMYKPuXV', '2004-12-07 11:42:22', '127.0.0.1');

# --------------------------------------------------------

#
# Table structure for table `swd_stat_account_dayly`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_stat_account_dayly`;
CREATE TABLE `swd_stat_account_dayly` (
  `fk_account` tinyint(4) NOT NULL default '0',
  `date` date NOT NULL default '0000-00-00',
  `subscribers` int(11) NOT NULL default '0',
  `unsubscribers` int(11) NOT NULL default '0',
  `sent_manual` int(11) NOT NULL default '0',
  `sent_sheduled` int(11) NOT NULL default '0',
  `sent_sequential` int(11) NOT NULL default '0',
  `sent_subscribe` int(11) NOT NULL default '0',
  `sent_unsubscribe` int(11) NOT NULL default '0',
  `sent_doubleoptin` int(11) NOT NULL default '0',
  PRIMARY KEY (`fk_account`,`date`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_stat_account_dayly`
#


# --------------------------------------------------------

#
# Table structure for table `swd_stat_dayly`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_stat_dayly`;
CREATE TABLE `swd_stat_dayly` (
  `date` date NOT NULL default '0000-00-00',
  `broadcast_starts` int(11) NOT NULL default '0',
  `is_adm_notif` tinyint(4) NOT NULL default '0',
  PRIMARY KEY (`date`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_stat_dayly`
#


# --------------------------------------------------------

#
# Table structure for table `swd_tosend`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:07 PM
#

DROP TABLE IF EXISTS `swd_tosend`;
CREATE TABLE `swd_tosend` (
  `fk_mess` int(11) NOT NULL default '0',
  `fk_user` int(11) NOT NULL default '0',
  `proc` tinyint(4) NOT NULL default '0',
  `paused` tinyint(4) NOT NULL default '0',
  PRIMARY KEY (`fk_mess`,`fk_user`),
  KEY `proc`(`proc`),
  KEY `procpaused`(`proc`,`paused`)
) TYPE=MyISAM;

#
# Dumping data for table `swd_tosend`
#


# --------------------------------------------------------

#
# Table structure for table `swd_user`
#
# Creation: Dec 04, 2004 at 07:07 PM
# Last update: Dec 04, 2004 at 07:11 PM
#

DROP TABLE IF EXISTS `swd_user`;
CREATE TABLE `swd_user` (
  `pk_user` int(11) default NULL auto_increment,
  `fk_account` int(11) NOT NULL default '0',
  `email` varchar(80) NOT NULL,
  `name` varchar(60) default NULL,
  `isact` tinyint(4) NOT NULL default '1',
  `datereg` date default NULL,
  `days` tinyint(4) default '0',
  `datelastsend` date default NULL,
  `messlastsend` int(11) default NULL,
  `countsend` int(11) NOT NULL default '0',
  `undelivered` tinyint(4) default NULL,
  `ip` varchar(15) default NULL,
  `unsubscribe` varchar(12) binary default NULL,
  PRIMARY KEY (`pk_user`),
  KEY `email`(`email`),
  KEY `unsubscribe`(`unsubscribe`),
  KEY `fk_account`(`fk_account`,`isact`),
  KEY `actaccountdays`(`fk_account`,`isact`,`days`),
  KEY `sequential`(`fk_account`,`messlastsend`,`datelastsend`,`days`,`isact`)
) TYPE=MyISAM AUTO_INCREMENT=2 ;

#
# Dumping data for table `swd_user`
#
INSERT INTO `swd_user` VALUES (1, 1, 'first@hotmail.com', 'First Subscriber', 0, '2005-05-03', 0,  NULL,  NULL, 0,  NULL,  NULL,  NULL);

DROP TABLE IF EXISTS `swd_bounce_account`;
CREATE TABLE `swd_bounce_account` (
  `pk_bounce_account` int(11) auto_increment,
  `pop3server` varchar(100) NOT NULL default '',
  `pop3user` varchar(100) NOT NULL default '',
  `pop3pass` varchar(50) NOT NULL default '',
  `pop3port` int(11) NOT NULL default '110',
  `isact` tinyint(4) NOT NULL default '1',
  `hardcount` tinyint(4) NOT NULL default '1',
  `softcount` tinyint(4) NOT NULL default '3',
  `deleteemails` char(2) default NULL,
  `bounceaction` tinyint(4) NOT NULL default '1',
  `isaddtoban` char(2) default NULL,
  PRIMARY KEY (`pk_bounce_account`)
) TYPE=MyISAM ;

DROP TABLE IF EXISTS `swd_bounce_allmessages`;
CREATE TABLE `swd_bounce_allmessages` (
  `messageid` varchar(150) NOT NULL default '',
  `date` datetime default NULL,
  PRIMARY KEY (`messageid`)
) TYPE=MyISAM;

DROP TABLE IF EXISTS `swd_bounce_banemails`;
CREATE TABLE `swd_bounce_banemails` (
  `email` varchar(150) NOT NULL default '',
  PRIMARY KEY (`email`)
) TYPE=MyISAM;

DROP TABLE IF EXISTS `swd_bounce_messages`;
CREATE TABLE `swd_bounce_messages` (
  `pk_bounce_message` int(11) NOT NULL auto_increment,
  `message_key` varchar(80) NOT NULL default '',
  `date` datetime NOT NULL,
  `email` varchar(80) NOT NULL default '',
  `action` tinyint(4) NOT NULL default '0',
  `status` varchar(9) default NULL,
  `reason` text,
  `fk_bounce_account` int(11) default NULL,
  `hardsoft` tinyint(4) NOT NULL default '0',
  `countprospects` int(11) NOT NULL default '0',
  PRIMARY KEY (`pk_bounce_message`),
  KEY `email`(`email`,`action`),
  UNIQUE KEY `message_key`(`message_key`),
  KEY `fk_bounce_account`(`fk_bounce_account`)
) TYPE=MyISAM;

