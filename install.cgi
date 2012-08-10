#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01.06                                                    #
# Developed by Kostya Ursalov, Andrey Stepanyuk,Dick Sсhiferly       #
# http://fump.biz http://goo.gl/A33qk                                #
# Last modified 10/07/2012                                           #
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
# Version 5.01.06                                                    #
# Last modified 09/08/2012                                           #
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
					#enable UTF support	
					$db->{'mysql_enable_utf8'} = 1;
				    	$db->do('SET NAMES utf8');

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

CREATE TABLE IF NOT EXISTS `swd_account` (
  `pk_account` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `isact` tinyint(4) NOT NULL DEFAULT '1',
  `descr` varchar(150) COLLATE utf8_unicode_ci DEFAULT NULL,
  `position` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pk_account`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=2 ;

--
-- Dumping data for table `swd_account`
--

INSERT INTO `swd_account` (`pk_account`, `name`, `isact`, `descr`, `position`) VALUES
(1, 'sample', 0, NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `swd_attach`
--

CREATE TABLE IF NOT EXISTS `swd_attach` (
  `pk_attach` int(11) NOT NULL AUTO_INCREMENT,
  `filename` varchar(80) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `data` longblob NOT NULL,
  `fk_mess` int(11) NOT NULL DEFAULT '0',
  `len` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pk_attach`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_bounce_account`
--

CREATE TABLE IF NOT EXISTS `swd_bounce_account` (
  `pk_bounce_account` int(11) NOT NULL AUTO_INCREMENT,
  `pop3server` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `pop3user` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `pop3pass` varchar(50) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `pop3port` int(11) NOT NULL DEFAULT '110',
  `isact` tinyint(4) NOT NULL DEFAULT '1',
  `hardcount` tinyint(4) NOT NULL DEFAULT '1',
  `softcount` tinyint(4) NOT NULL DEFAULT '3',
  `deleteemails` char(2) COLLATE utf8_unicode_ci DEFAULT NULL,
  `bounceaction` tinyint(4) NOT NULL DEFAULT '1',
  `isaddtoban` char(2) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk_bounce_account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_bounce_allmessages`
--

CREATE TABLE IF NOT EXISTS `swd_bounce_allmessages` (
  `messageid` varchar(150) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`messageid`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_bounce_banemails`
--

CREATE TABLE IF NOT EXISTS `swd_bounce_banemails` (
  `email` varchar(150) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`email`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_bounce_messages`
--

CREATE TABLE IF NOT EXISTS `swd_bounce_messages` (
  `pk_bounce_message` int(11) NOT NULL AUTO_INCREMENT,
  `message_key` varchar(80) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `date` datetime NOT NULL,
  `email` varchar(80) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `action` tinyint(4) NOT NULL DEFAULT '0',
  `status` varchar(9) COLLATE utf8_unicode_ci DEFAULT NULL,
  `reason` text COLLATE utf8_unicode_ci,
  `fk_bounce_account` int(11) DEFAULT NULL,
  `hardsoft` tinyint(4) NOT NULL DEFAULT '0',
  `countprospects` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pk_bounce_message`),
  UNIQUE KEY `message_key` (`message_key`),
  KEY `email` (`email`,`action`),
  KEY `fk_bounce_account` (`fk_bounce_account`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_brodcastlog`
--

CREATE TABLE IF NOT EXISTS `swd_brodcastlog` (
  `pk_broadcastlog` int(11) NOT NULL AUTO_INCREMENT,
  `date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `procnomber` tinyint(4) NOT NULL DEFAULT '0',
  `pid` varchar(6) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `log` text COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`pk_broadcastlog`),
  KEY `procnomber` (`procnomber`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_conf`
--

CREATE TABLE IF NOT EXISTS `swd_conf` (
  `pk_conf` varchar(30) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `conf_value` text COLLATE utf8_unicode_ci,
  `discr` text COLLATE utf8_unicode_ci,
  `fk_account` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pk_conf`,`fk_account`),
  KEY `pk_conf` (`pk_conf`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- Dumping data for table `swd_conf`
--

INSERT INTO `swd_conf` (`pk_conf`, `conf_value`, `discr`, `fk_account`) VALUES
('VERSION', '5.1', NULL, 0),
('defname', 'Friend', NULL, 1),
('subscribeemail', 'subscribe@domain.com', NULL, 1),
('pop3server', 'pop3.yourdomain.com', NULL, 1),
('pop3user', 'johndoe', NULL, 1),
('pop3pass', '12345', NULL, 1),
('pop3port', '110', NULL, 1),
('fromname', 'Your Name', NULL, 1),
('fromemail', 'noreply@yourdomain.com', NULL, 1),
('isaddunsubscrlink', 'on', NULL, 1),
('isnotifsubscr', 'on', NULL, 1),
('isnotifunsubscr', 'on', NULL, 1),
('isdoi', 'on', NULL, 1),
('doiconfurl', 'http://www.yourdomain.com', NULL, 1),
('ispop3', '', NULL, 1),
('redirsub', 'http://www.yourdomain.com', NULL, 1),
('redirrem', 'http://www.yourdomain.com', NULL, 1),
('PID', '0', NULL, 0),
('timebroadcast', '1053972878', NULL, 0),
('sendmail', '/usr/sbin/sendmail', NULL, 0),
('modsend', 'sendmail', NULL, 0),
('smtp', 'localhost', NULL, 0),
('adminname', 'Admin', NULL, 0),
('adminemail', 'yourname@yourdomain.com', NULL, 0),
('statbyemail', 'on', NULL, 0),
('enablelog', 'on', NULL, 0),
('sendsubscr', 'on', NULL, 1),
('sendunsubscr', 'on', NULL, 1),
('maxlim', '23', NULL, 0),
('timecorr', '+00:00', NULL, 0),
('replyto', 'noreply@yourdomain.com', NULL, 1),
('uppercase', '', NULL, 1),
('messlogging', 'on', NULL, 1),
('ispurge', '', NULL, 1),
('banmails', '', NULL, 1),
('banmailserror', '', NULL, 1),
('defcharset', '', NULL, 1),
('no_uppercase', '', NULL, 1),
('adminpwd', 'fumpdev123', NULL, 0),
('serverurl', 'http://fumpservice.test/cgi-bin/fumpdev/', NULL, 0),
('splashsettings', 'daily_stats', NULL, 0);

-- --------------------------------------------------------

--
-- Table structure for table `swd_doi`
--

CREATE TABLE IF NOT EXISTS `swd_doi` (
  `pk_doi` int(11) NOT NULL AUTO_INCREMENT,
  `ran` char(10) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`pk_doi`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_doiaccounts`
--

CREATE TABLE IF NOT EXISTS `swd_doiaccounts` (
  `fk_doi` int(11) NOT NULL DEFAULT '0',
  `fk_account` int(11) NOT NULL DEFAULT '0',
  `fk_user` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`fk_doi`,`fk_account`),
  KEY `fk_user` (`fk_user`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_doppar`
--

CREATE TABLE IF NOT EXISTS `swd_doppar` (
  `fk_fields` int(11) NOT NULL DEFAULT '0',
  `fk_user` int(11) NOT NULL DEFAULT '0',
  `value` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`fk_fields`,`fk_user`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_fields`
--

CREATE TABLE IF NOT EXISTS `swd_fields` (
  `pk_fields` int(11) NOT NULL AUTO_INCREMENT,
  `fieldname` varchar(40) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `fk_account` int(11) NOT NULL DEFAULT '0',
  `is_req` int(11) NOT NULL DEFAULT '0',
  `rang` tinyint(4) NOT NULL DEFAULT '1',
  `type` enum('text','textarea') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'text',
  PRIMARY KEY (`pk_fields`),
  KEY `fieldaddr` (`fieldname`,`fk_account`,`pk_fields`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=16 ;

--
-- Dumping data for table `swd_fields`
--

INSERT INTO `swd_fields` (`pk_fields`, `fieldname`, `fk_account`, `is_req`, `rang`, `type`) VALUES
(7, 'Date', 1, 0, 4, 'text'),
(6, 'City', 1, 0, 3, 'text'),
(5, 'Address', 1, 0, 2, 'text'),
(8, 'Date2', 1, 0, 5, 'text'),
(9, 'sex', 1, 0, 6, 'text'),
(10, 'sname', 1, 0, 7, 'text'),
(11, 'state', 1, 0, 8, 'text'),
(12, 'url1', 1, 0, 9, 'text'),
(13, 'url2', 1, 0, 10, 'text'),
(14, 'Zip', 1, 0, 11, 'text'),
(15, 'Country', 1, 0, 1, 'text');

-- --------------------------------------------------------

--
-- Table structure for table `swd_links`
--

CREATE TABLE IF NOT EXISTS `swd_links` (
  `pk_link` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `redirect_link` text COLLATE utf8_unicode_ci NOT NULL,
  `fk_account` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pk_link`),
  KEY `fk_account` (`fk_account`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=3 ;

--
-- Dumping data for table `swd_links`
--

INSERT INTO `swd_links` (`pk_link`, `name`, `redirect_link`, `fk_account`) VALUES
(1, 'Test1', 'http://www.yahoo.com', 1),
(2, 'Test 2', 'http://www.microsoft.com', 1);

-- --------------------------------------------------------

--
-- Table structure for table `swd_link_clicks`
--

CREATE TABLE IF NOT EXISTS `swd_link_clicks` (
  `pk_link_click` int(11) NOT NULL AUTO_INCREMENT,
  `fk_link` int(11) DEFAULT '0',
  `fk_user` int(11) DEFAULT '0',
  `fk_mess` int(11) DEFAULT '0',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`pk_link_click`),
  KEY `fk_account` (`fk_user`,`fk_mess`,`fk_link`),
  KEY `timestamp` (`timestamp`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_log`
--

CREATE TABLE IF NOT EXISTS `swd_log` (
  `pk_log` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `log` text COLLATE utf8_unicode_ci,
  PRIMARY KEY (`pk_log`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_mess`
--

CREATE TABLE IF NOT EXISTS `swd_mess` (
  `pk_mess` int(11) NOT NULL AUTO_INCREMENT,
  `fk_account` int(11) NOT NULL DEFAULT '0',
  `subject` varchar(100) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `mess` text COLLATE utf8_unicode_ci,
  `messhtml` text COLLATE utf8_unicode_ci,
  `type` enum('text','html','mixed') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'text',
  `defmesstype` tinyint(4) DEFAULT '1',
  `typesend` enum('manual','doi','auto','senddat','subscribe','unsubscribe') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'manual',
  `days` int(11) DEFAULT NULL,
  `senddat` date DEFAULT NULL,
  `sent` int(11) DEFAULT '0',
  `datesend` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `priority` int(11) DEFAULT NULL,
  `encoding` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  `issendnow` tinyint(4) NOT NULL DEFAULT '0',
  `saveinhistory` varchar(2) COLLATE utf8_unicode_ci DEFAULT NULL,
  `messrss` text COLLATE utf8_unicode_ci,
  `rsslink` text COLLATE utf8_unicode_ci,
  `fromnamemess` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  `fromemailmess` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  `usefrom` tinyint(4) DEFAULT '0',
  `repeating` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`pk_mess`),
  KEY `typesend` (`typesend`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=6 ;

--
-- Dumping data for table `swd_mess`
--

INSERT INTO `swd_mess` (`pk_mess`, `fk_account`, `subject`, `mess`, `messhtml`, `type`, `defmesstype`, `typesend`, `days`, `senddat`, `sent`, `datesend`, `priority`, `encoding`, `issendnow`, `saveinhistory`, `messrss`, `rsslink`, `fromnamemess`, `fromemailmess`, `usefrom`, `repeating`) VALUES
(2, 1, 'Test sequential message for [FULLNAME]', '[FULLNAME] will extract and print your prospect''s whole name (i.e. ''Mr. [FULLNAME],'' will print ''Mr. John Doe'', if your prospect''s name is John Doe). \r\n[EMAIL] will extract and print your prospect''s e-mail address (i.e. ''Your e-mail address is [EMAIL]'' will output ''Your e-mail address is john@domain.com'', if your prospect''s e-mail address is john@domain.com. \r\n[DATE] will print current date in dd/mm/yyyy format. \r\n[DATE+32d] [DATE-32d] [DATE+1m] [DATE-1m] [DATE+1y] [DATE-1y] will print corrected current date in dd/mm/yyyy format. \r\nExtra merge field words\r\n[ADD15] - Country \r\n[ADD5] - Address \r\n[ADD6] - City \r\n[ADD7] - Date \r\n[ADD8] - Date2 \r\n[ADD9] - sex \r\n[ADD10] - sname \r\n[ADD11] - state \r\n[ADD12] - url1 \r\n[ADD13] - url2 \r\n[ADD14] - Zip\r\n', '', 'text', 1, 'auto', 1, NULL, 0, '2012-08-05 15:03:58', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, 0),
(5, 1, 'Sample manual message  for [FULLNAME]', 'This is the Sample manual message  for [FULLNAME]', '', 'text', 1, 'manual', 0, NULL, 0, '2012-08-05 15:03:58', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, 0),
(3, 1, 'Subscribe message', 'Put your subscribe message here', '', 'text', 1, 'subscribe', 0, NULL, 0, '2012-08-05 15:03:58', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, 0),
(4, 1, 'Unsubscribe message', 'Your message', '', 'text', 1, 'unsubscribe', 0, NULL, 0, '2012-08-05 15:03:58', NULL, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, 0),
(1, 1, 'Please confirm your subscription', 'To confirm your subscription, click on the link below \r\n(you must be connected to the internet at the time):\r\n\r\n[CONFIRM_URL]\r\n\r\nIf you did not make the request, there is no need\r\nto take any further action.\r\n', '', 'text', 1, 'doi', 0, NULL, 0, '2012-08-05 15:03:58', 2, NULL, 0, NULL, NULL, NULL, NULL, NULL, 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `swd_process_loc`
--

CREATE TABLE IF NOT EXISTS `swd_process_loc` (
  `pk_process_loc` int(11) NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `PID` varchar(8) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  `procnomber` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`pk_process_loc`),
  KEY `procnomber` (`procnomber`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- Table structure for table `swd_senthistory`
--

CREATE TABLE IF NOT EXISTS `swd_senthistory` (
  `fk_user` int(11) NOT NULL,
  `fk_mess` int(11) NOT NULL,
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`fk_user`,`fk_mess`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_sentlog`
--

CREATE TABLE IF NOT EXISTS `swd_sentlog` (
  `fk_user` int(11) NOT NULL DEFAULT '0',
  `fk_mess` int(11) NOT NULL DEFAULT '0',
  `date` datetime DEFAULT NULL,
  PRIMARY KEY (`fk_user`,`fk_mess`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_ses`
--

CREATE TABLE IF NOT EXISTS `swd_ses` (
  `pk_ses` int(11) NOT NULL AUTO_INCREMENT,
  `ran` varchar(25) COLLATE utf8_unicode_ci NOT NULL DEFAULT '0',
  `date` datetime DEFAULT NULL,
  `host` varchar(14) COLLATE utf8_unicode_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`pk_ses`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=7 ;

--
-- Dumping data for table `swd_ses`
--

INSERT INTO `swd_ses` (`pk_ses`, `ran`, `date`, `host`) VALUES
(6, 'zMSdm_Btrep6s8gV1JwMjDCWN', '2012-08-09 04:09:36', '212.92.251.3');

-- --------------------------------------------------------

--
-- Table structure for table `swd_stat_account_dayly`
--

CREATE TABLE IF NOT EXISTS `swd_stat_account_dayly` (
  `fk_account` tinyint(4) NOT NULL DEFAULT '0',
  `date` date NOT NULL DEFAULT '0000-00-00',
  `subscribers` int(11) NOT NULL DEFAULT '0',
  `unsubscribers` int(11) NOT NULL DEFAULT '0',
  `sent_manual` int(11) NOT NULL DEFAULT '0',
  `sent_sheduled` int(11) NOT NULL DEFAULT '0',
  `sent_sequential` int(11) NOT NULL DEFAULT '0',
  `sent_subscribe` int(11) NOT NULL DEFAULT '0',
  `sent_unsubscribe` int(11) NOT NULL DEFAULT '0',
  `sent_doubleoptin` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`fk_account`,`date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_stat_dayly`
--

CREATE TABLE IF NOT EXISTS `swd_stat_dayly` (
  `date` date NOT NULL DEFAULT '0000-00-00',
  `broadcast_starts` int(11) NOT NULL DEFAULT '0',
  `is_adm_notif` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`date`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_tosend`
--

CREATE TABLE IF NOT EXISTS `swd_tosend` (
  `fk_mess` int(11) NOT NULL DEFAULT '0',
  `fk_user` int(11) NOT NULL DEFAULT '0',
  `proc` tinyint(4) NOT NULL DEFAULT '0',
  `paused` tinyint(4) NOT NULL DEFAULT '0',
  PRIMARY KEY (`fk_mess`,`fk_user`),
  KEY `proc` (`proc`),
  KEY `procpaused` (`proc`,`paused`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `swd_user`
--

CREATE TABLE IF NOT EXISTS `swd_user` (
  `pk_user` int(11) NOT NULL AUTO_INCREMENT,
  `fk_account` int(11) NOT NULL DEFAULT '0',
  `email` varchar(80) COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(60) COLLATE utf8_unicode_ci DEFAULT NULL,
  `isact` tinyint(4) NOT NULL DEFAULT '1',
  `datereg` date DEFAULT NULL,
  `days` int(11) DEFAULT '0',
  `datelastsend` date DEFAULT NULL,
  `messlastsend` int(11) DEFAULT NULL,
  `countsend` int(11) NOT NULL DEFAULT '0',
  `undelivered` tinyint(4) DEFAULT NULL,
  `ip` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  `unsubscribe` varchar(12) COLLATE utf8_unicode_ci DEFAULT NULL,
  `messageformat` tinyint(4) NOT NULL DEFAULT '0',
  `fk_affiliate` int(11) DEFAULT NULL,
  `fromname` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  `referrer_link` varchar(12) COLLATE utf8_unicode_ci DEFAULT NULL,
  `sequence_repeat` int(11) NOT NULL DEFAULT '0',
  `fromemail` varchar(80) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`pk_user`),
  KEY `email` (`email`),
  KEY `unsubscribe` (`unsubscribe`),
  KEY `fk_account` (`fk_account`,`isact`),
  KEY `fk_affiliate` (`fk_affiliate`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci AUTO_INCREMENT=2 ;

--
-- Dumping data for table `swd_user`
--

INSERT INTO `swd_user` (`pk_user`, `fk_account`, `email`, `name`, `isact`, `datereg`, `days`, `datelastsend`, `messlastsend`, `countsend`, `undelivered`, `ip`, `unsubscribe`, `messageformat`, `fk_affiliate`, `fromname`, `referrer_link`, `sequence_repeat`, `fromemail`) VALUES
(1, 1, 'first@hotmail.com', 'First Subscriber', 0, '2005-05-03', 0, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL, NULL, NULL, 0, NULL);

