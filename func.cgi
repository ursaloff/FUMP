#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01.03                                                    #
# Last modified 03/06/2009                                           #
######################################################################
use lib('lib');
use DBI;
use dbfunc;
use POSIX;
use MIME::Lite;
use Time::Local;
use Net::SMTP;
use Fcntl qw(:DEFAULT :flock);
local $USER,$PASS;
local %CONF;

$c_file="cnf.rd";
$cfg_psd="Follow Up Mailing List Processor Installation - SellWide.com";
%TYPESEND=(html=>"text/html",text=>"text/plain");
%ENCODINGS=(
	'UTF-8'	=>'UTF-8',
	'iso-8859-1'=>'Western (latin)', 
	'iso-8859-2'=>'Central European (iso-8859-2)', 
	'x-mac-ce'=>'Central European (Mac CE)', 
	'windows-1250'=>'Central European (Windows-1250)',
	'iso-8859-5'=>'Cyrrillic (iso-8859-5)', 
	'koi8-r' => 'Cyrrillic (koi8-r)',
	'koi8-u' => 'Cyrrillic Ukraine (koi8-u)',
	'x-mac-cyrillic'=>'Cyrillic (Mac)' ,
	'windows-1251' => 'Cyrillic (Windows-1251)',
	'iso-8859-7'=>'Greek (iso-8859-7)',
	'x-mac-greek' =>'Greek (Mac)', 
	'windows-1253'=>'Greek (Windows-1253)',
	'windows-1250'=>'Windows-1250',
	'windows-1252'=>'Windows-1252',
	'Shift_JIS'=>'Japanies (Shift_JIS)',
	'iso-2022-jp'=>'Japanies (iso-2022-jp)',
	'EUC-JP'=>'Japanies  (EUC-JP)', 
	'big5' => 'Chinese Traditional (Big5)', 
	'gb2312'=> 'Simplified Chinese');
%PRIORITY=(''=>'Default',3=>"Normal",2=>"High",1=>"Low");
%rss_languages = (
    'af'    => 'Afrikaans',
    'sq'    => 'Albanian',
    'eu'    => 'Basque',
    'be'    => 'Belarusian',
    'bg'    => 'Bulgarian',
    'ca'    => 'Catalan',
    'zh-cn' => 'Chinese (Simplified)',
    'zh-tw' => 'Chinese (Traditional)',
    'hr'    => 'Croatian',
    'cs'    => 'Czech',
    'da'    => 'Danish',
    'nl'    => 'Dutch',
    'nl-be' => 'Dutch (Belgium)',
    'nl-nl' => 'Dutch (Netherlands)',
    'en'    => 'English',
    'en-au' => 'English (Australia)',
    'en-bz' => 'English (Belize)',
    'en-ca' => 'English (Canada)',
    'en-ie' => 'English (Ireland)',
    'en-jm' => 'English (Jamaica)',
    'en-nz' => 'English (New Zealand)',
    'en-ph' => 'English (Phillipines)',
    'en-za' => 'English (South Africa)',
    'en-tt' => 'English (Trinidad)',
    'en-gb' => 'English (United Kingdom)',
    'en-us' => 'English (United States)',
    'en-zw' => 'English (Zimbabwe)',
    'fo'    => 'Faeroese',
    'fi'    => 'Finnish',
    'fr'    => 'French',
    'fr-be' => 'French (Belgium)',
    'fr-ca' => 'French (Canada)',
    'fr-fr' => 'French (France)',
    'fr-lu' => 'French (Luxembourg)',
    'fr-mc' => 'French (Monaco)',
    'fr-ch' => 'French (Switzerland)',
    'gl'    => 'Galician',
    'gd'    => 'Gaelic',
    'de'    => 'German',
    'de-at' => 'German (Austria)',
    'de-de' => 'German (Germany)',
    'de-li' => 'German (Liechtenstein)',
    'de-lu' => 'German (Luxembourg)',
    'el'    => 'Greek',
    'hu'    => 'Hungarian',
    'is'    => 'Icelandic',
    'in'    => 'Indonesian',
    'ga'    => 'Irish',
    'it'    => 'Italian',
    'it-it' => 'Italian (Italy)',
    'it-ch' => 'Italian (Switzerland)',
    'ja'    => 'Japanese',
    'ko'    => 'Korean',
    'mk'    => 'Macedonian',
    'no'    => 'Norwegian',
    'pl'    => 'Polish',
    'pt'    => 'Portuguese',
    'pt-br' => 'Portuguese (Brazil)',
    'pt-pt' => 'Portuguese (Portugal)',
    'ro'    => 'Romanian',
    'ro-mo' => 'Romanian (Moldova)',
    'ro-ro' => 'Romanian (Romania)',
    'ru'    => 'Russian',
    'ru-mo' => 'Russian (Moldova)',
    'ru-ru' => 'Russian (Russia)',
    'sr'    => 'Serbian',
    'sk'    => 'Slovak',
    'sl'    => 'Slovenian',
    'es'    => 'Spanish',
    'es-ar' => 'Spanish (Argentina)',
    'es-bo' => 'Spanish (Bolivia)',
    'es-cl' => 'Spanish (Chile)',
    'es-co' => 'Spanish (Colombia)',
    'es-cr' => 'Spanish (Costa Rica)',
    'es-do' => 'Spanish (Dominican Republic)',
    'es-ec' => 'Spanish (Ecuador)',
    'es-sv' => 'Spanish (El Salvador)',
    'es-gt' => 'Spanish (Guatemala)',
    'es-hn' => 'Spanish (Honduras)',
    'es-mx' => 'Spanish (Mexico)',
    'es-ni' => 'Spanish (Nicaragua)',
    'es-pa' => 'Spanish (Panama)',
    'es-py' => 'Spanish (Paraguay)',
    'es-pe' => 'Spanish (Peru)',
    'es-pr' => 'Spanish (Puerto Rico)',
    'es-es' => 'Spanish (Spain)',
    'es-uy' => 'Spanish (Uruguay)',
    'es-ve' => 'Spanish (Venezuela)',
    'sv'    => 'Swedish',
    'sv-fi' => 'Swedish (Finland)',
    'sv-se' => 'Swedish (Sweden)',
    'tr'    => 'Turkish',
    'uk'    => 'Ukranian'
		 );

@backup_tables=qw(
account
attach
bounce_account
bounce_allmessages
bounce_banemails
bounce_messages
brodcastlog
changepref
conf
doi
doiaccounts
doppar
fields
link_clicks
links
log
mess
process_loc
senthistory
sentlog
ses
stat_account_dayly
stat_dayly
tosend
user
signatures
);		 
#Templates
%SIGNATURES_CONTENT=();
%URLS_CONTENT=();
%FILES_CONTENT=();
$PersonalDirectories='personal';
$TempatesDir=$PersonalDirectories.'/signatures';
$TempatesSubscribeDir=$PersonalDirectories.'/templthankyou';
$TempatesDoiDir=$PersonalDirectories.'/templconfirm';
$TempatesPrefDir=$PersonalDirectories.'/templpersonal';
$BroadcastLogFile="broadcast.log";
$LANG_ALREADY_LOADED=0;

#Timeout between broadcasts in minutes
$TIMEOUT=5;
$VERSION="5.1";
{
my @d = localtime(time());
$YEAR_NOW= $d[5]+1900;
}
########
%CASH_ACCOUNT_FIELDS=();
%CASH_SEQUENSE=();
%CASH_USER_TABLE_FILEDS = ();

sub get_meta_charset{
	$CONF{defcharset}='utf-8' unless(length($CONF{defcharset}));
	return qq|<meta http-equiv="Content-Type" content="text/html; charset=$CONF{defcharset}" />|;
}

sub FillTextFromFile{
	my $text=shift;
	$text=~s/(\[LOAD_FROM_FILE_.+?\])/&LoadContentFromFile($1)/gse;
	return $text;
}
sub FillTextFromURL{
	my $text=shift;
	$text=~s/(\[LOAD_FROM_URL_.+?\])/&LoadContentFromURL($1)/gse;
	return $text;
	
}
sub LoadContentFromURL{
	my $tag=shift;
	$tag=~/\[LOAD_FROM_URL_(.+)\]/;
	my $url=$1;
	return "" unless length($url);
	return $URLS_CONTENT{$url} if exists($URLS_CONTENT{$url});
	eval('require LWP::UserAgent');
	if($@){
		# $URLS_CONTENT{$url}="$LNG{ERROR_LOADING_FROM_URL} $url : \n $@";
		$URLS_CONTENT{$url}="$LNG{ERROR_LOADING_FROM_URL}: \n $@";
		return $URLS_CONTENT{$url};
	}
	
	my $ua = LWP::UserAgent->new;
	$ua->agent('Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.8.0.6) Gecko/20060728 Firefox/1.5.0.6');
       	$ua->timeout(5);
       	my $response = $ua->get($url);
       	if ($response->is_success) {
	   	 $URLS_CONTENT{$url}=$response->content;  # or whatever
       	} else {
	   	 # $URLS_CONTENT{$url}= "$LNG{ERROR_LOADING_FROM_URL} $url ". $response->status_line;
	   	 $URLS_CONTENT{$url}= "$LNG{ERROR_LOADING_FROM_URL}";
       	}
	return $URLS_CONTENT{$url};
	
}
sub LoadContentFromFile{
	my $tag=shift;
	$tag=~/\[LOAD_FROM_FILE_(.+)\]/;
	my $file=$1;
	return "\nError! Incorrect tag $tag\n" unless length($file);
	$file="${TempatesDir}/$file.txt";
	return "\nError! File $file not exists\n" unless(-f $file);
	return $FILES_CONTENT{$file} if(exists($FILES_CONTENT{$file}));
	open(FILE,"$file")||return "\nError! Can not open file $file: $!\n";
	my $data;
	while(<FILE>){$data.=$_;}
	close(FILE);
	$data=~s/(\[LOAD_FROM_FILE_.+?\])/THIS TAG IN FILE IS STRIPPED/gs;
	$FILES_CONTENT{$file}=$data;
	return $data;
}
###################
sub IncreaseBroadcasterCounter{
	my $what=shift;
	if (GetSQLCount("SELECT * FROM ${PREF}stat_dayly  WHERE `date`=CURDATE()")){
		$db->do("UPDATE ${PREF}stat_dayly SET $what=$what+1 WHERE `date`=CURDATE()");
	}else{
		$db->do("INSERT INTO ${PREF}stat_dayly (date,$what) VALUES ($NOW,1)");
	}
}
###################
sub IncreaseAccountCounter{
	my $what=shift;
	my $account=shift;
	return unless $account;
	return unless $what;
	if (GetSQLCount("SELECT * FROM ${PREF}stat_account_dayly  WHERE `date`=CURDATE() AND fk_account=?",$account)){
		$db->do("UPDATE ${PREF}stat_account_dayly SET $what=$what+1  WHERE `date`=CURDATE() AND fk_account=?",undef,$account);
	}else{
		$db->do("INSERT INTO ${PREF}stat_account_dayly (fk_account,date,$what) VALUES (?,$NOW,1)",undef,$account);
	}
}
###################
sub CanIWork{
	my $procno=shift; # 0 if main process;
	my $im_first=shift;
	if  (!$procno && $im_first){
		my $dt=select_one_db("SELECT CURRENT_DATE( ) AS dt");
		unless($CONF{repare_date} eq $dt->{$dt}){
			save_config(0,'repare_date',$dt->{dt});
			my @t=map{$PREF.$_}@backup_tables;
			my $t=join(", ",@t);
			$db->do("REPAIR TABLE $t");
		}
		$db->do("LOCK TABLES ${PREF}process_loc READ");
		if(GetSQLCount("SELECT * FROM ${PREF}process_loc WHERE `date` > NOW() - INTERVAL  $TIMEOUT MINUTE")){
			$db->do("UNLOCK TABLES");
			exit;
		}
		$db->do("UNLOCK TABLES");
		$db->do("LOCK TABLES ${PREF}process_loc WRITE");
		$db->do("DELETE FROM ${PREF}process_loc");
		$db->do("INSERT INTO `${PREF}process_loc` ( `date` , `PID` , `procnomber` ) VALUES ( NOW( ) , ? , ?)",undef,$$,$procno);
		$db->do("UNLOCK TABLES");
	}elsif  (!$procno && !$im_first){
		$db->do("LOCK TABLES ${PREF}process_loc READ");
		unless(GetSQLCount("SELECT * FROM ${PREF}process_loc WHERE `PID`=?",$$)){
			$db->do("UNLOCK TABLES");
			doMonitor(0, "Someone is kill my PID abnormal exit");
			exit;
		}
		$db->do("UNLOCK TABLES");
		$db->do("LOCK TABLES ${PREF}process_loc WRITE");
		$db->do("UPDATE `${PREF}process_loc` SET `date`=NOW() WHERE `PID`=?",undef,$$);
		$db->do("UNLOCK TABLES");
	}elsif($procno && $im_first){
		$db->do("LOCK TABLES ${PREF}process_loc READ");
		if(GetSQLCount("SELECT * FROM ${PREF}process_loc WHERE `procnomber`=?",$procno)){
			$db->do("UNLOCK TABLES");
			doMonitor($procno, "Some child proccess is still working with my number $procno : abnormal exit");
			exit;					
		}
		$db->do("LOCK TABLES ${PREF}process_loc WRITE");
		$db->do("INSERT INTO `${PREF}process_loc` ( `date` , `PID` , `procnomber` ) VALUES ( NOW( ) , ? , ?)",undef,$$,$procno);
		$db->do("UNLOCK TABLES");
	}else{
		$db->do("LOCK TABLES ${PREF}process_loc READ");
		unless(GetSQLCount("SELECT * FROM ${PREF}process_loc WHERE `PID`=?",$$)){
			$db->do("UNLOCK TABLES");
			doMonitor($procno, "Someone is kill my PID abnormal exit");
			exit;			
		}
		$db->do("LOCK TABLES ${PREF}process_loc WRITE");
		$db->do("UPDATE `${PREF}process_loc` SET `date`=NOW() WHERE `PID`=?",undef,$$);		
		$db->do("UNLOCK TABLES");
	}
}
sub doMonitor{
	my $procno=shift;
	my $log=shift;
	$db->do("INSERT INTO ${PREF}brodcastlog  (date,   procnomber,   pid,   log) VALUES ($NOW,?,?,?)",undef,$procno,$$,$log);
	if($CONF{save_broadcast_log}){
		if(open(FILE,">>$BroadcastLogFile")){
			unless ($^O=~/win/i){
				unless(flock(FILE, LOCK_EX())){
					$db->do("INSERT INTO ${PREF}brodcastlog  (date,   procnomber,   pid,   log) VALUES ($NOW,?,?,?)",undef,$procno,$$,"Can not lock file $BroadcastLogFile");
					close(FILE);
					return;
				}
			}
			chomp($log);
			print FILE "".GetDate()."\t$procno\t$$\t$log\n";
			close(FILE);
		}
	}
}
###############################
sub doLog{
	my $log=shift;
	$db->do("INSERT INTO ${PREF}log (date,log) VALUES ($NOW,?)",undef,$log) if $CONF{enablelog};
}
###############################
sub sequre
{
	local $_=$_[0];
	s/&/&amp;/g;
	s/"/&quot;/g;
	s/>/&gt;/g;
	s/</&lt;/g;
	if($_[1]!=1){
		s/\n/<br>\n/g;}
	return $_;
}
#####################
sub unsequre
{
	local $_=$_[0];
	s/&quot;/"/g;
	s/&gt;/>/g;
	s/&lt;/</g;
	if($_[1]!=1){
		s/<br>\n/\n/g;
	}
	s/&amp;/&/g;
	return $_;
}
#####################
sub AddToSend{
	my $user=shift;
	my $mess=shift;
	my $sql="REPLACE INTO ${PREF}tosend (fk_user,fk_mess) VALUES (?,?)";
	$db->do($sql,undef,$user,$mess);
	ErrorDBI(0,$sql);	
}
sub MessageWasSent{
	my $user=shift;
	my $mess=shift;
	$db->do("UPDATE ${PREF}mess SET sent=sent+1 WHERE pk_mess=?",undef,$mess);
	$db->do("UPDATE ${PREF}user SET countsend=countsend+1 WHERE pk_user=?",undef,$user);

}
#####################
sub CanISendForUser{
	my $user=shift;
	my $mess=shift;
	my $conf=shift;
	return 1 unless($conf->{messlogging});
	if (GetSQLCount("SELECT * FROM ${PREF}sentlog WHERE fk_mess=? AND fk_user=?",$mess,$user)>0){
		return 0;
	}else{
		return 1;
	}
}
#############
sub LogMessage{
	my $user=shift;
	my $mess=shift;
	my $conf=shift;
	if($conf->{messlogging}){
		$db->do("REPLACE INTO ${PREF}sentlog (fk_user,fk_mess,date) VALUES (?,?,$NOW)",undef,$user,$mess)
	}
	#unless (GetSQLCount("SELECT * FROM ${PREF}sentlog WHERE fk_mess=? AND fk_user=?",$mess,$user)>0){
		
	#}
}
###################
sub DeleteUser{
	my $userid=shift;
	$db->do("DELETE FROM ${PREF}user WHERE pk_user=?",undef,$userid);
	$db->do("DELETE FROM ${PREF}tosend WHERE fk_user=?",undef,$userid);
	$db->do("DELETE FROM ${PREF}sentlog  WHERE fk_user=?",undef,$userid);
	$db->do("DELETE FROM ${PREF}senthistory  WHERE fk_user=?",undef,$userid);
	$db->do("DELETE FROM ${PREF}doiaccounts  WHERE fk_user=?",undef,$userid);		
	$db->do("DELETE FROM ${PREF}doppar  WHERE fk_user=?",undef,$userid);
	$db->do("UPDATE ${PREF}user SET fk_affiliate=0 WHERE fk_affiliate=?",undef,$userid);
}###################
sub InactivateUser{
	my $userid=shift;
	$db->do("UPDATE ${PREF}user SET isact=0 WHERE pk_user=?",undef,$userid);
}
#####################
sub save_config{
	my $account=shift;	
	my $key=shift;
	my $value=shift;
	my $count=GetSQLCount("SELECT * FROM ${PREF}conf WHERE pk_conf=? AND fk_account=?",$key,$account);
	if ($count){
		update_db("${PREF}conf",{conf_value =>$value},{pk_conf=>$key,fk_account=>$account});
	}else{
		insert_db("${PREF}conf",{conf_value =>$value,pk_conf=>$key,fk_account=>$account});
	}
	$CONF{$key}=$value;
}
#####################
sub loadCONF{
	my $account=shift;
	my %conf;
	my $where;
	if ($account){
		$where= " where fk_account in (0,$account) ";
	}else{
		$where= " where fk_account=0 ";
	}
	my $sql="select * from ${PREF}conf $where";
	my $out=$db->prepare($sql);
	$out->execute();
	my %output;
	while (%output=%{$out->fetchrow_hashref}){
		$conf{$output{pk_conf}}=$output{conf_value};
	}
	return %conf;
}
#####################
sub db_prepare{
	open(FILE,$c_file) || die "Can not open file $c_file : $!";
	my $cr=<FILE>;
	close(FILE);
	$cr=unfs($cr,$cfg_psd x ceil(length($cr)/length($cfg_psd)));
	my %ps;
	my @sr=split(/;/,$cr);
	foreach (@sr) { /(.*?):(.*)/;$ps{$1}=$2 }
	$DATABASE=$ps{_db};	$USER=$ps{_us};	$PASS=$ps{_pass};$PREF=$ps{_pref};
	$BDHOST=$ps{_host};
	$BDHOST='localhost' unless $BDHOST;
	$db = DBI->connect("DBI:mysql:database=$DATABASE;host=$BDHOST",$USER,$PASS) ||
	die "We are not connected to database $DATABASE \n\n Error: $DBI::err : $DBI::errstr ";
	#enable UTF support	
	$db->{'mysql_enable_utf8'} = 1;
    	$db->do('SET NAMES utf8');
	my $where;
	if (exists $PAR{account}){
		$where= " where fk_account in (0,$PAR{account}) ";
	}else{
		$where= " where fk_account=0 ";
	}
	##load conf
	my $sql="select * from ${PREF}conf $where";
	my $out=$db->prepare($sql);
	$out->execute();
	my %output;
	while (%output=%{$out->fetchrow_hashref}){
		$CONF{$output{pk_conf}}=$output{conf_value};
	}
	#die scalar(keys(%CONF));
	$NOW=GetNow($CONF{timecorr});
	$MY_TIME=time+TimeToSec($CONF{timecorr});
	#load accounts
	my $sql="select * from ${PREF}account ORDER by position ASC, name ASC";
	my $out=$db->prepare($sql);
	$out->execute();
	my %output;
	@ACCOUNT_ORDER=();
	while (%output=%{$out->fetchrow_hashref}){
		push(@ACCOUNT_ORDER,$output{pk_account});
		$ACCOUNT{$output{pk_account}}=$output{name};
	}
	unless($LANG_ALREADY_LOADED){
		$CONF{langnow}="en" unless $CONF{langnow};
		loadlang($CONF{langnow},0);
		if($CONF{langnow} ne 'en'){
			loadlang('en',1,1);
		}
		$LANG_ALREADY_LOADED=1;
	}
	return $db;
}
sub loadlang{
	my $langnow=shift;
	my $nocheck=shift;
	my $notoverwrite=shift;
	open(FILE,"shabl/lang/$langnow.txt") || die "Can not find language file shabl/lang/$langnow.txt";
	my $line;
	my $texts;
	my $texts_now=0;
	my $text_now;
	my $text_key_now;
	#First line - lang defenition
	my $lng_line=<FILE>;
	chomp($lng_line);
	my ($lng_name,$lng_charset)=split(/\t/,$lng_line);
	unless ($notoverwrite){
		$CONF{defcharset}=$lng_charset unless length($CONF{defcharset});
	}
	$CONF{langnowname}=$lng_name;
	my $already_exists=0;
	while(<FILE>){
		unless($texts_now){
			if(/____STARTTEXTS____/){
				$texts_now=1;	
				next;
			}
			chomp;
			$line++;
			next if /^\s*#/;
			my ($key,$value)=split(/\t/);
			next unless $key;
			unless($notoverwrite){
				unless($nocheck){
					die "Dublicate lang key '$key' entry in file shabl/lang/$langnow.txt line $line" if exists($LNG{$key});
				}
			}
			if($notoverwrite){
				$LNG{$key}="$value" unless exists($LNG{$key});
			}else{
				$LNG{$key}="$value";
			}			
		}else{
			if(/\[T_([A-Z0-9_]+)\]/){
				$text_key_now=$1;
				if(exists $LNG{$text_key_now}){
					$already_exists=1;
					
				}
			}elsif(/\[\/T_([A-Z0-9_]+)\]/){
				$text_key_now="";
				$already_exists=0;
			}else{
				next if ($notoverwrite && $already_exists);
				$LNG{$text_key_now}.=$_;
			}
		}
	}
#	map{$LNG{$_}="|$LNG{$_}|"}keys %LNG;
#	while($texts=~/\[T_([A-Z0-9_]+)\](.*)\[\/T_([A-Z0-9_]+)\]/s){
#		die "Dublicate lang key '$1' entry in file shabl/lang/$langnow.txt - TEXTS" if exists($LNG{$key});
#		$LNG{$1}=$2;
#		
#	}
	
	
}
###################
#Checking
###################
sub checkemail {
	my $email = shift;
	my $isreq=shift;
	$isreq="1" if ($isreq eq '');
	if ($isreq == 0){
		return 1 if ($email eq '');
	}
	if ($email =~ /(@.*@)|(\.\.)|(@\.)|(\.@)|(^\.)/ || $email !~ /^.+\@(\[?)[a-zA-Z0-9\-\.]+\.([a-zA-Z0-9]{2,4}|[0-9]{1,3})(\]?)$/) {
		return 0;
	}
	else {
		return 1;
	}
}
########
sub check_url{
	my $url=shift;
	my $isreq=shift;
	$isreq="1" if ($isreq eq '');
	unless ($isreq){
		return 1 unless $url;
	}
	if ($url=~m#^([a-z]+):\/\/+#){
		$url=~s#^([a-z]+):\/\/+##;
		if ($1){
			unless (($1 eq 'http') || ($1 eq 'https')){
				return 0;
			}
		}
	}
	return 0 if $url=~/ /;
	if ($isreq){
		return 0 unless $url;
	}
	return 0 if $url=~/\.\.|\(|\)/;
	return 1;
}
###################
#END Checking
###################
#############
sub printenv{
	foreach (sort keys %ENV){
		print "\$ENV{$_}=$ENV{$_}<br>\n"
	}
}
sub unfsmy{
	my $what=shift;
	$what=~tr/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/DNfeQS5Ouj6rMkIg9PwTXHzC1Vc3vEA8nxlLF7KYbsUmJhZ4WoRqiGpy0aBd2t/;
	$what =~ s/_([\dA-Fa-f][\dA-Fa-f])/pack ("C", hex ($1))/eg;
	return $what;
}
##############
sub fisher_yates_shuffle {
	my $array = shift;
	my $i;
	for ($i = @$array; --$i; ) {
		my $j = int rand ($i+1);
		next if $i == $j;
		@$array[$i,$j] = @$array[$j,$i];
	}
}
sub unfs {
	local($text, $key) = @_;
	local($response) = '';
	local($i, $j, $num, $result);
	local($text_len) = length($text);
	local($key_len) = length($key);
	for ($i = $text_len - 1; $i >= 0; --$i) {
		$num = ord(chop($text));
		if ($num == 127) { $num = 58 }
		$num -= 32;
		for ($j = $i; $j < $key_len; $j += $text_len) {
			$num -= ord(substr($key, $j, 1)) + $key_len;
		}
		$num = $num % 95 + 32;
		$result .= pack("c", $num);
	}
	return($result);
} 
sub fs {
	local($text, $key) = @_;
	local($response) = '';
	local($i, $j, $num, $result);
	local($text_len) = length($text);
	local($key_len) = length($key);
	for ($i = 0; $i < $text_len; ++$i) {
		$num = ord(chop($text)) - 32;
		for ($j = $i; $j < $key_len; $j += $text_len) {
			$num += ord(substr($key, $j, 1)) + $key_len;
		}
		$num = $num % 95 + 32;
		if ($num == 58) { $num = 127 };
		$result .= pack("c", $num);
	}
	return($result);
}
##################
#TIME SYNCHRONISATION
##################
sub GetStartDay{
	my $now=shift;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =  localtime($now);
	return timelocal(0,0,0,$mday,$mon,$year);
}
###################
sub GetNow{
	my $now;
	my $add=shift;
	return ("NOW()") if ($add eq "");
	if ($add=~s/^-//){
		$now="DATE_SUB(NOW(), INTERVAL '$add' HOUR_MINUTE)";
	}else{
		$now="DATE_ADD(NOW(), INTERVAL '$add' HOUR_MINUTE)";
	}
	return $now;
}
#############################
sub TimeToSec{
	my $time=shift;
	my $k=1;
	if ($time=~s/^-//){
		$k=-1;
	}else{
		$k=1;
	}
	chomp ($time);
	my ($h,$m,$s)=split(/:/,$time);
	return ($s+$m*60+$h*60*60)*$k;
}
##################################################
sub GetDate{
	my $noadd=shift;
	my $add;
	$add=0 if $noadd;
	$add=TimeToSec($CONF{timecorr}) unless $noadd;
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time + $add);
	$year += 1900;
	$mon++;
	$mon = sprintf("%02d", $mon);
	$mday = sprintf("%02d", $mday);
	$hour = sprintf("%02d", $hour);
	$min = sprintf("%02d", $min);
	$sec = sprintf("%02d", $sec);
	return "$year-$mon-$mday $hour:$min:$sec";
}
################
sub mimeformat {
	my($filename) = @_;
	my($result);
	my %extensions = ( 
		gif      => ['image/GIF' , 'base64'],
		txt      => ['text/plain' , '8bit'],
		com      => ['text/plain' , '8bit'],
		doc      => ['application/msword', 'base64'],
		class    => ['application/octet-stream' , 'base64'],
		htm      => ['text/html' , '8bit'],
		html     => ['text/html' , '8bit'],
		htmlx    => ['text/html' , '8bit'],
		htx      => ['text/html' , '8bit'],
		jpg      => ['image/jpeg' , 'base64'],
		pdf      => ['application/pdf' , 'base64'],
		mpeg     => ['video/mpeg' , 'base64'],
		mov      => ['video/quicktime' , 'base64'],
		exe      => ['application/octet-stream' , 'base64'],
		zip      => ['application/zip' , 'base64'],
		au       => ['audio/basic' , 'base64'],
		mid      => ['audio/midi' , 'base64'],
		midi     => ['audio/midi' , 'base64'],
		wav      => ['audio/x-wav' , 'base64'],
		tar      => ['application/tar' , 'base64']
	); # %extensions
	if ($filename =~ /.*\.(.+)$/) {
		$ext = $1;
	} # if
	if (exists($extensions{$ext})) {
		$result = $extensions{$ext};
	} # if
	else {
		$result = ['BINARY', 'base64'];
	} # else
	return $result;
}
############################
sub MIMEsendto{
	my $to=shift;
	my $msg=shift;
	if(length($CONF{returnpath})){
		$msg->replace('Return-Path'=>$CONF{returnpath});
	}
	if(length($CONF{errorsto})){
		$msg->replace('Errors-To'=>$CONF{errorsto});
	}
	my $data=$msg->as_string;
	my $leng=length($data);
	if ($CONF{modsend} eq 'SMTP'){
		my $FROM,$TO;
		($FROM,$TO)=($msg->get("From"),$msg->get("TO"));
		$FROM=~/([a-zA-Z0-9_.\-]+@[a-zA-Z0-9_.\-]+)/;
		$FROM=$1;
		if($CONF{smtpuseadminemail} and checkemail($CONF{smtpfromemail})){
			$FROM=$CONF{smtpfromemail};
		}
		$TO=~/([a-zA-Z0-9_.\-]+@[a-zA-Z0-9_.\-]+)/;
		$TO=$1;
		my $smtp;
		my $maxattempts=100;
		my $attemp;
		while(!($smtp = Net::SMTP->new($CONF{smtp}))){
			$attemp++;
			sleep(1);
			if ($attemp>$maxattempts){
				exit;
			}
		}
		if($CONF{smtpauth}){
			unless($smtp->auth($CONF{smtpusername},$CONF{smtppassword})){
				doLog("SMTP auth error user: $CONF{smtpusername}");
				return 0;
			}
		}
		$smtp->mail($FROM);
		$smtp->to($TO);
		$smtp->data();
		$smtp->datasend($data);
		$smtp->dataend();
		$smtp->quit;
	}else{
		my $Fflag="";
		if($CONF{issendmailf} and checkemail($CONF{sendmailaddress})){
			$Fflag=" -f$CONF{sendmailaddress}";	
		}
		open(SENDMAIL, "|".$CONF{sendmail}.' -i -t '.$Fflag);
		#sometimes additional line breaks happens 
		$data=~s/\r\n/\n/g;
		print SENDMAIL $data;
		close(SENDMAIL);
	}
	return $leng;
}
sub Add_User_Fields{
	my $userrow=shift;
	foreach my $key(keys %$userrow){
		next unless $key=~/^field(\d+)$/;
		$userrow->{doppar}{$1}=$userrow->{$key};
	}
	$userrow->{referrer_link}=create_referrer_link($userrow);
	$userrow->{unsubscribe}=create_unsubscribe_link($userrow);

	return $userrow;
}
#######################
sub loaduser{
	my $userid=shift;
	my $userrow=shift;
	my $account=shift;
	if(defined $userrow){
		$userrow=Add_User_Fields($userrow);
		return $userrow;
	}
	if($account){
		my @where=();
		push(@where,['pk_user','=',$userid]);
		my $sql=AccountUsersSQL($account,\@where,{},1,0);
		$userrow=select_one_db($sql);
		$userrow=Add_User_Fields($userrow);
		return $userrow;
	}
	#only user ID
	my $user;
	$user=select_one_db("SELECT *,UNIX_TIMESTAMP(datereg) AS unixregdate FROM ${PREF}user WHERE pk_user=?",$userid);
	$sql="SELECT * FROM ${PREF}doppar WHERE fk_user=?";
	my $out=$db->prepare($sql);
	$out->execute($userid);
	while (my %output=%{$out->fetchrow_hashref}){
		$user->{doppar}{$output{fk_fields}}=$output{value};	
	}
	#generating unique ID
	$user->{referrer_link}=create_referrer_link($user);
	$user->{unsubscribe}=create_unsubscribe_link($user);
	return $user;
}
#######################
sub load_mess{
	my $mess=shift;
#	DATE_FORMAT(senddat, '%Y-%b-%d' ) as senddat, 
	my $SQL=<<ALL__;
SELECT 
	${PREF}mess.*,
	DAYOFMONTH(senddat) as n_day,
	MONTH(senddat) as n_month,
	YEAR(senddat) as n_year
FROM ${PREF}mess 	
WHERE pk_mess=?
ALL__
	$mess_ref=select_one_db($SQL,$mess);
	$mess_ref->{ATTACH}=load_mess_attachment($mess);
	return $mess_ref;
}
#########################
sub load_mess_attachment{
	my $pk_mess=shift;
	my %attach;
	my $out=$db->prepare("SELECT * FROM ${PREF}attach WHERE fk_mess=?");
	$out->execute($pk_mess);
	while (my %output=%{$out->fetchrow_hashref}){
		my $id=$output{pk_attach};delete($output{pk_attach});
		$attach{$id}=\%output;
	}
	return \%attach;
}
######################
sub save_user_parametr{
	my $field=shift;
	my $user=shift;
	my $value=shift;
	return if $field=~/[^0-9]/;
	return if $user=~/[^0-9]/;
	if ($value eq ""){
		$db->do("DELETE FROM ${PREF}doppar WHERE fk_fields=? AND fk_user=?",undef,$field,$user);
		return;
	}
	my $count=GetSQLCount("SELECT * FROM ${PREF}doppar WHERE fk_fields=? AND fk_user=?",$field,$user);
	if ($count){
		update_db("${PREF}doppar",{value =>$value},{fk_fields=>$field,fk_user=>$user});
	}else{
		insert_db("${PREF}doppar",{value =>$value,fk_fields=>$field,fk_user=>$user});
	}
}
#################
sub load_account_fields{
	my $account=shift;
	return (@{$CASH_ACCOUNT_FIELDS{$account}}) if(exists $CASH_ACCOUNT_FIELDS{$account});
	my @FIELDS;	
	my $sql="SELECT * from ${PREF}fields WHERE fk_account=? ORDER BY `rang` ASC ";
	my $out=$db->prepare($sql);
	$out->execute($account);
	&Error($sql);
	my %output;
	while (%output=%{$out->fetchrow_hashref}){
		push(@FIELDS,{key=>$output{pk_fields},name=>$output{fieldname},rang=>$output{rang},type=>$output{type},is_req=>$output{is_req}});
	}
	$CASH_ACCOUNT_FIELDS{$account}=\@FIELDS;
	return 	@FIELDS;
}
sub preparename{
	my $user=shift;
	my $noucase=shift;
	#$user=~s/[^A-Za-z0-9\-.]/ /g;
	$user=~s/^ +//;
	$user=~s/ +$//;
	$user=~s/\s+/ /g;
	my @words=split(/ /,$user);
	unless($noucase){
		@words=map{ucfirst(lc($_))}@words;
	}
	my $name=join(' ',@words);
	return $name;
}
sub prepareemail{
	return lc(shift);
}
sub is_email_banned{
	my $email=shift;
	my $banlist=shift;
	my @tmpbans=split(/\n/,$banlist);
	my @bans;
	foreach my $line(@tmpbans){
		chomp($line);
		$line=~s/\s//g;
		next unless length($line);
		return 1 if $email=~/$line/i;
	}
	return 0;
}
sub create_unsubscribe_link{
	my $user=shift;
	return $user->{unsubscribe} if $user->{unsubscribe};
	my @chars=('a'..'z','A'..'Z',0..9,'_');
	my $ran=join("", @chars[map{rand @chars}(1..12)]);
	while(GetSQLCount("Select * from ${PREF}user WHERE unsubscribe=?",$ran)){
		$ran=join("", @chars[map{rand @chars}(1..12)]);
	}
	update_db("${PREF}user",{unsubscribe=>$ran},{pk_user=>$user->{pk_user}});
	$user->{unsubscribe}=$ran;
	return $ran;
}
sub create_referrer_link{
	my $user=shift;
	return $user->{referrer_link} if $user->{referrer_link};
	my @chars=('a'..'z','A'..'Z',0..9,'_');
	my $ran=join("", @chars[map{rand @chars}(1..12)]);
	while(GetSQLCount("Select * from ${PREF}user WHERE referrer_link=?",$ran)){
		$ran=join("", @chars[map{rand @chars}(1..12)]);
	}
	update_db("${PREF}user",{referrer_link=>$ran},{pk_user=>$user->{pk_user}});
	$user->{referrer_link}=$ran;
	return $ran;
}
###############
#Encodings
###############
sub prepare_words{
	my $words=shift;
	my $encoding=shift;
	my $Def_Enc=shift;
	return $words unless $encoding;
	if ($words=~/([ \t\n!-<>-~])/){
		(my $noteng=$words)=~s/[ \t\n!-<>-~]//g;
		return $words if (length($noteng)==0); 
		return $words if (length($words)==0);
		my $ENC='';
		my $encoded = "";
		if ((int(length($noteng)/length($words)*100)>10) || length($words) > 25){
			$ENC="B";
			$encoded=my_encode_base64($words,$encoding);				
		}else{
			$encoded=my_encode_qp($words,$encoding);	
			$ENC="Q";
		}
		return $encoded;
		#return "=?$encoding?$ENC?$encoded?=";
	}else{
		return $words;	
	}
}
#########################
sub my_encode_base64 {
	my $res = "";
	my $eol = "\n";
	pos($_[0]) = 0;        ### thanks, Andreas!
	while ($_[0] =~ /(.{1,45})/gs) {
		$res .= substr(pack('u', $1), 1);
		chop($res);
	}
	my $encoding=$_[1];
	$res =~ tr#` -_#AA-Za-z0-9+/#;
	### Fix padding at the end:
	my $padding = (3 - length($_[0]) % 3) % 3;
	$res =~ s/.{$padding}$/'=' x $padding/e if $padding;
	### Break encoded string into lines of no more than 76 characters each:
	$res =~ s/(.{1,60})/$1$eol/g if (length $eol);
	my @res=split(/\n/,$res);
	@res=map{"=?$encoding?B?$_?="}@res;
	return join("\n",@res);
}
sub my_encode_qp {
	my $res = shift;
	my $encoding=shift;
	local($_);
	$res =~ s/([^ \t\n!-<>-~])/sprintf("=%02X", ord($1))/eg;  ### rule #2,#3
	$res =~ s/([ \t]+)$/
	join('', map { sprintf("=%02X", ord($_)) }
	split('', $1)
	)/egm;                        ### rule #3 (encode whitespace at eol)

	### rule #5 (lines shorter than 76 chars, but can't break =XX escapes:
	my $brokenlines = "";
	$brokenlines .= "$1=\n" while $res =~ s/^(.{70}([^=]{2})?)//; ### 70 was 74
	$brokenlines =~ s/=\n$// unless length $res; 
	"=?$encoding?Q?$brokenlines$res?=";
}
################################
sub ProcessDate{
	my $corr=shift;
	my $unixregdate=shift;
	my $seccor;
	if ($corr=~/([+\-]\d+)(y|d|m)/){
		$seccor=$1;
		my $koeff=$2;
		my $corrcoeff;
		if ($koeff eq 'd'){
			$corrcoeff=60*60*24
		}elsif($koeff eq 'm'){
			$corrcoeff=60*60*24*30
		}elsif($koeff eq 'y'){
			$corrcoeff=60*60*24*365
		}
		$corr=$corr*$corrcoeff;
	}
	my $corrtime;
	unless($unixregdate){
		$corrtime=$MY_TIME+$corr;
	}else{
		$corrtime=$unixregdate+$corr;
	}
	unless($CONF{date_format}){
		$CONF{date_format}='%m/%d/%Y';
	}
	return strftime($CONF{date_format},localtime($corrtime));
}
sub PersonalizeText{
	my $text=shift;
	my $conf=shift;
	my $user=shift;
	my $mess=shift;
	my $from_name=shift;
	my $from_email=shift;
	unless (defined $from_email){
		($from_name,$from_email)=GetFromNameAndEmail($user,$conf,$mess);	
	}	
	my $userfullname=$user->{name};
	$text=FillTextFromFile($text);
	$text=FillTextFromURL($text);
	$userfullname=$conf->{defname} unless $userfullname;
	my $userfistname;
	if ($userfullname=~/ /){
		$userfullname=~/(.*?) /;
		$userfistname=$1;
	}else{
		$userfistname=$userfullname;
	}
	$userfistname=ucfirst($userfistname) unless $conf->{no_uppercase};
	$userfullname=ucfirst($userfullname) unless $conf->{no_uppercase};
	my $unsrun=create_unsubscribe_link($user);
	my $unslink="$conf->{serverurl}register.cgi?un=$unsrun";
	my $modify_link="$conf->{serverurl}pref.cgi?u=$unsrun";
	my $RSS_link="$conf->{serverurl}rss.cgi?u=$unsrun";
	my $HTML_link="$conf->{serverurl}rss.cgi?u=$unsrun&m=web";
	my $unixregdate=$user->{unixregdate};
	$text=~s/\[FROMNAME\]/$from_name/g;
	$text=~s/\[FROMEMAIL\]/$from_email/g;
	$text=~s/\[FULLNAME\]/$userfullname/g;
	$text=~s/\[FIRSTNAME\]/$userfistname/g;
	$text=~s/\[EMAIL\]/$user->{email}/g;
	$text=~s/\[ADD(\d+)\]/$user->{doppar}{$1}/g;
	$text=~s/\[DATE(.*?)\]/ProcessDate($1)/ge;
	$text=~s/\[REG_DATE(.*?)\]/ProcessDate($1,$unixregdate)/ge;
	$text=~s/\[IP\]/$user->{ip}/g;		
	$text=~s/\[LINK(\d+)\]/$conf->{serverurl}r.cgi?u=$unsrun&l=$1&m=$mess->{pk_mess}/g;
	$text=~s/\[SUBSCR_ACCOUNT(\d+)\]/$conf->{serverurl}register.cgi?act=m&list=$1&sub=$unsrun/g;
	$text=~s/\[UNSUBSCRIBE_LINK\]/$unslink/g;
	$text=~s/\[REFERRER_TRACKING_ID\]/$user->{referrer_link}/g;
	$text=~s/\[MODIFY_CONTACT_INFO\]/$modify_link/g;
	$text=~s/\[SUBSCRIBER_ID\]/$user->{pk_user}/g;
	$text=~s/\[SUBSCRIBER_UUI\]/$unsrun/g;
	$text=~s/\[RSS_LINK\]/$RSS_link/g;
	$text=~s/\[HTML_LINK\]/$HTML_link/g;
	return $text;
}


sub GetMessText{
	my ($user,$conf,$mess,$account);
	$user=shift;
	$conf=shift;
	$mess=shift;
	my $is_download=shift;
	$account=$user->{fk_account};	
	if($mess->{type}=~/mixed/i){
		if(length($mess->{mess}) and length($mess->{messhtml})){
			#nothing to do
		}elsif(length($mess->{messhtml})){
			$mess->{type}='html'
		}else{
			$mess->{type}='text'
		}
	}
	#Message format
	if($mess->{type}=~/mixed/i){
		if($user->{messageformat}==1){
			#user TEXT
			$mess->{type}='text';			
		}elsif($user->{messageformat}==2){
			#user HTML
			$mess->{type}='html';			
		}else{
			#user DEFAULT
			if($mess->{defmesstype}==2){
				#DEFAULT message TYPE is "HTML"
				$mess->{type}='html';
			}else{
				$mess->{type}='text';
			}
		}
	}
	my $messtext,$messsubject;	
	if($mess->{type}=~/text/){
		$messtext=$mess->{mess};
		$messtext=~s/\[SIGNATURE_([a-zA-Z_0-9]+?)\]/&LoadSignature($1,0)/gse;	
	}else{
		$messtext=$mess->{messhtml};
		$messtext=~s/\[SIGNATURE_([a-zA-Z_0-9]+?)\]/&LoadSignature($1,1)/gse;			
	}
	return($messtext);
}
sub LoadSignature{
	my $name=shift;
	my $ishtml=shift;

	unless(exists($SIGNATURES_CONTENT{$name})){
		my $sign=select_one_db("SELECT * FROM ${PREF}signatures WHERE name=?",$name);
		$SIGNATURES_CONTENT{$name}=[$sign->{sig_text},$sign->{sig_html}];
	}
	return $ishtml?$SIGNATURES_CONTENT{$name}->[1]:$SIGNATURES_CONTENT{$name}->[0];
}
sub GetFromNameAndEmail{
	my $user=shift;
	my $conf=shift;
	my $mess=shift;
	my $from_name=$conf->{fromname};
	my $from_email=$conf->{fromemail};
	if($mess->{usefrom}==1){
		#Override name and email from message
		if (length($mess->{fromemailmess}) and checkemail($mess->{fromemailmess})){
			return ($mess->{fromnamemess},$mess->{fromemailmess});
		}
	}elsif($mess->{usefrom}==2){
		#From prospect preferences
		if (length($user->{fromemail}) and checkemail($user->{fromemail})){
			return ($user->{fromname},$user->{fromemail});
		}
	}elsif($mess->{usefrom}==3){
		#From referrer contact information
		if (length($user->{affiliate1email}) and checkemail($user->{affiliate1email})){
			return ($user->{affiliate1name},$user->{affiliate1email});
		}
	}
	return($from_name,$from_email);

}
################################
sub GetMessForUser{
	my ($user,$conf,$mess,$account);
	$user=shift;
	$conf=shift;
	$mess=shift;
	my $is_download=shift;
	$account=$user->{fk_account};
	$messtext=GetMessText($user,$conf,$mess);
	$messsubject=$mess->{subject};
	my ($from_name,$from_email)=GetFromNameAndEmail($user,$conf,$mess);
	$messtext   =PersonalizeText($messtext   ,$conf,$user,$mess,$from_name,$from_email);
	$messsubject=PersonalizeText($messsubject,$conf,$user,$mess,$from_name,$from_email);
	if ($conf->{addunsubscribelinkauto}){
		my $unsrun=create_unsubscribe_link($user);
		my $unslink;	
		$unslink="$conf->{serverurl}register.cgi?unsubscribe=$unsrun";
		unless ($mess->{typesend} eq 'unsubscribe' or $mess->{typesend} eq 'doi'){
			if ($mess->{type} eq 'text'){
				$messtext.="\n\n$LNG{TO_UNSUBSCRIBE_CLICK_LINK_BELOW} $unslink";
				
			}else{
				my $link="\n\n<P>$LNG{TO_UNSUBSCRIBE_CLICK_LINK_BELOW} <a href=\"$unslink\">$unslink</a></P>";
				if ($messtext=~/<\/BODY>/i){
					$messtext=~s/<\/BODY>/$link <\/BODY>/i;
				}elsif($messtext=~/<\/HTML>/i){
					$messtext=~s/<\/HTML>/$link <\/HTML>/i;
				}else{
					$messtext.=$link;
				}
			}
		}
	}
	
	my $from,$to;
	#let's set tefault encoding - utf-8 for sending messages
	$mess->{encoding}="utf-8" unless $mess->{encoding}; 
	$from=prepare_words($from_name,$mess->{encoding})." <$from_email>" if $from_name;
	$from="$from_email" unless $from_name;
	#Bug fix with dublicate sending
	$user->{name}=~s/[;,:~#*~?\\}\]\[{]/ /g;
	
	$to = prepare_words($user->{name},$mess->{encoding})." <$user->{email}>" if $user->{name};
	$to = "$user->{email}" unless $user->{name};
	my $msg = new MIME::Lite 
	From    =>$from,
	To      =>$to,
	Subject =>prepare_words($messsubject,$mess->{encoding}),
	Type    =>$TYPESEND{$mess->{type}},
	Data    =>$messtext;
	$msg->attr("content-type.charset" => $mess->{encoding}) if $mess->{encoding};
	$msg->attr("X-Priority" => "$mess->{priority} ($PRIORITY{$mess->{priority}})") if $mess->{priority};
	foreach (keys %{$mess->{ATTACH}}){
		my($mime)=&mimeformat($mess->{ATTACH}{$_}{filename});
		$msg->attach
		(	Type =>$mime->[0],
			Encoding =>$mime->[1],
			Id =>"<$mess->{ATTACH}{$_}{filename}>",
			Filename =>$mess->{ATTACH}{$_}{filename},
			Data => $mess->{ATTACH}{$_}{data},
		);	
	}
	if ($conf->{replyto}){
		$msg->add('Reply-To'  => $conf->{replyto});
	}
	my %to_log=(
		manual=>'sent_manual',
		doi=>'sent_doubleoptin', 
		auto=>'sent_sequential', 
		senddat=>'sent_sheduled',
		'subscribe'=>'sent_subscribe', 
		'unsubscribe'=>'sent_unsubscribe'
	);
	#unless($is_download){
	if(exists($to_log{$mess->{typesend}})){
		IncreaseAccountCounter($to_log{$mess->{typesend}},$account);	
	}
	if($mess->{saveinhistory}){
		$db->do("REPLACE INTO ${PREF}senthistory (fk_user,fk_mess,date) VALUES (?,?,$NOW)",undef,$user->{pk_user},$mess->{pk_mess});
	}
	#}
	return $msg;
}
##########################
sub registerUSER{
	my $Account=shift;
	my $Email=shift;
	my $Name=shift;
	my $Add_Fields_ref=shift;
	my $Fields_names_ref=shift;
	my $messageformat=shift;
	my $optional_subscribe=shift;
	my $fromname=shift;
	my $fromemail=shift;
	my $referrer_link=shift;
	my $all_fields=shift;
	$messageformat=0 unless ($messageformat==1 or $messageformat==2);
	my %CONF=loadCONF($Account);
	my %accounts=();
	my @addaccount=();
	my @addaccount_unsubscribe=();	
	my @addaccount_suspend=();	
   my @addaccount_lock=();
	my $USER_ID;
	if ($CONF{ADD_ACCOUNTS}){
		@addaccount=split(/\|/,$CONF{ADD_ACCOUNTS});
	}
	my %add_account_subscribe=();
	map{$add_account_subscribe{$_}=1}@addaccount;
	if (defined($optional_subscribe)){
		map{$add_account_subscribe{$_}=1}@$optional_subscribe;
	}
	@addaccount=sort keys %add_account_subscribe;
	if($CONF{unsub_account_all}){
		map{push(@addaccount_unsubscribe,$_) if($_ ne $Account)}keys %ACCOUNT;	
	}elsif($CONF{ADD_ACCOUNTS_UNSUBSCRIBE}){
		map{push(@addaccount_unsubscribe,$_) if($_ ne $Account)}split(/\|/,$CONF{ADD_ACCOUNTS_UNSUBSCRIBE});
	}
	if($CONF{suspend_account_all}){
		map{push(@addaccount_suspend,$_) if($_ ne $Account)}keys %ACCOUNT;	
	}elsif($CONF{ADD_ACCOUNTS_SUSPEND}){
		map{push(@addaccount_suspend,$_) if($_ ne $Account)}split(/\|/,$CONF{ADD_ACCOUNTS_SUSPEND});
	}
	if($CONF{lock_account_all}){
		map{push(@addaccount_lock,$_) if($_ ne $Account)}keys %ACCOUNT;	
	}elsif($CONF{ADD_ACCOUNTS_LOCK}){
		map{push(@addaccount_lock,$_) if($_ ne $Account)}split(/\|/,$CONF{ADD_ACCOUNTS_LOCK});
	}   
	my %doi;
	$doi{$Account}=$CONF{isdoi};
	my $keynow,$isact,$doikey;
	my $randoi;
	my @chars=('a'..'z','A'..'Z',0..9,'_');
	$randoi=join("", @chars[map{rand @chars}(1..10)]);
	my $count=GetSQLCount("SELECT * FROM ${PREF}user WHERE email=? AND fk_account=?",$Email,$Account);
	my $redirtoaccount;
	$Email=prepareemail($Email);
	$Name=preparename($Name,$CONF{no_uppercase});
	if(length($fromemail) and checkemail($fromemail)){
		$fromname=preparename($fromname,$CONF{no_uppercase});
		$fromemail=prepareemail($fromemail);
	}else{
		$fromemail='';
		$fromname='';
	}
	my $fk_affiliate=0;
	if(length($referrer_link)){
		my $ref=select_one_db("SELECT * FROM ${PREF}user WHERE referrer_link = ?",$referrer_link);
		$fk_affiliate = $ref->{pk_user} if $ref->{pk_user};
	}
	unless($count){
		$isact=0 if $doi{$Account};
		$isact=1 unless $doi{$Account};
		my $isactmess="";
		$isactmess.="with double opt in" if $doi{$Account};
		$keynow=insert_db("${PREF}user",{email=>$Email,name=>$Name,isact=>$isact,days=>0,fk_account=>$Account,ip=>$ENV{REMOTE_ADDR},messageformat=>$messageformat,fromname=>$fromname,fromemail=>$fromemail,fk_affiliate=>$fk_affiliate});
		IncreaseAccountCounter('subscribers',$Account);	
		$USER_ID=$keynow;
		doLog("User $Name ($Email) was registered to account $ACCOUNT{$Account} $isactmess");
		$db->do("UPDATE ${PREF}user SET datereg=$NOW WHERE pk_user=?",undef,$keynow);
		foreach my $dp_key(keys %{$Add_Fields_ref}){
			save_user_parametr($dp_key,$keynow,$Add_Fields_ref->{$dp_key});
		}
		if($doi{$Account}){
			$doikey=insert_db("${PREF}doi",{ran=>$randoi});
			#REPLACE instead update
			my $sql="REPLACE INTO ${PREF}doiaccounts (fk_doi,fk_account,fk_user) VALUES (?,?,?)";
			$db->do($sql,undef,$doikey,$Account,$keynow);
			&Error;
			#insert_db("${PREF}doiaccounts",{fk_doi=>$doikey,fk_account=>$Account,fk_user=>$keynow});
			$redirtoaccount=$Account;
			my $address=$ENV{HTTP_HOST};
			my $scriptdir=$ENV{SCRIPT_NAME};
			(my $src=$scriptdir)=~s#[^/]*$##;
			my $url_redir="$CONF{serverurl}register.cgi?id=$randoi&act=$redirtoaccount";
			$mess=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend='doi'",$redirtoaccount);
			#unless ($mess->{mess}=~/\[CONFIRM_URL\]/){
			unless ($mess->{pk_mess}){				
				$mess->{mess}=<<ALL__;
To confirm your subscription, click on the link below 
(you must be connected to the internet at the time):

[CONFIRM_URL]

If you did not make the request, there is no need
to take any further action.
ALL__
				$mess->{subject}="Please confirm your subscription";
				$mess->{type}='text';
				$mess->{typesend}='doi';
			}else{
				$mess=load_mess($mess->{pk_mess});	
	
			}
			$mess->{mess}=~s/\[CONFIRM_URL\]/$url_redir/g;
			$mess->{messhtml}=~s/\[CONFIRM_URL\]/$url_redir/g;
			$user=loaduser($USER_ID,undef,$Account);
			$msg=GetMessForUser($user,\%CONF,$mess,$redirtoaccount);
			MIMEsendto($Email,$msg);
			MessageWasSent($USER_ID,$mess->{pk_mess});
		}else{ 	#if($doi{$Account}){
			if($CONF{sendsubscr}){
				my $messages=select_one_db("SELECT * FROM ${PREF}mess WHERE fk_account=? AND typesend=?",$Account,'subscribe');
				if ($messages->{pk_mess}){
					$mess=load_mess($messages->{pk_mess});
					$user=loaduser($USER_ID,undef,$Account);
					$msg=GetMessForUser($user,\%CONF,$mess,$Account);
					my $leng=MIMEsendto($Email,$msg);
					MessageWasSent($USER_ID,$messages->{pk_mess});
				}
				
			}
		}	#End if($doi{$Account}){
		if($CONF{isnotifsubscr}){
			my $DOPPAR;
			if(%{$Add_Fields_ref}){
				$DOPPAR="\n=============================\n===Additional fields:\n=============================\n";
				#foreach my $dp_key(keys %{$Add_Fields_ref}){
				#	$DOPPAR.="$Fields_names_ref->{$dp_key}: $Add_Fields_ref->{$dp_key}\n";
				#}
				#
				foreach (@{$all_fields}){
					my $dp_key=$_->{key};
					$DOPPAR.="$Fields_names_ref->{$dp_key}: $Add_Fields_ref->{$dp_key}\n";
				}
			}
			$user=loaduser($USER_ID,undef,$Account);
			my $unsrun=create_unsubscribe_link($user);
			$unslink="$CONF{serverurl}register.cgi?unsubscribe=$unsrun";
			my $n=GetDate();
			$msg = new MIME::Lite 
			From    =>"FUMP Registration <$CONF{adminemail}>",
			To      =>"$CONF{adminname} <$CONF{adminemail}>",
			Subject =>"User $Email registered at the $ACCOUNT{$Account} account",
			Data    =>qq|Account: $ACCOUNT{$Account}\nName: $Name\nEmail: $Email\nUser ID: $USER_ID\nDate: $n\nUser IP: $ENV{REMOTE_ADDR}\n$DOPPAR\n\n Remove this prospect:\n $unslink\n\n----------\nPowered by Follow Up Mailing List Processor PRO $VERSION\n\n|;
			MIMEsendto($CONF{adminemail},$msg);

		}#End if($CONF{isnotifsubscr})
		foreach(@addaccount){
			next unless $_;
			my $count=GetSQLCount("SELECT * FROM ${PREF}user WHERE email=? AND fk_account=?",$Email,$_);
			next if $count;
			$isact=0 if $doi{$Account};
			$isact=1 unless $doi{$Account};
			$keynow=insert_db("${PREF}user",{email=>$Email,name=>$Name,isact=>$isact,days=>0,fk_account=>$_,ip=>$ENV{REMOTE_ADDR},fromname=>$fromname,fromemail=>$fromemail});
			loaduser($keynow);
			doLog("User $Name ($Email) was registered to account $ACCOUNT{$_}");
			IncreaseAccountCounter('subscribers',$_);
			$db->do("UPDATE ${PREF}user SET datereg=$NOW WHERE pk_user=?",undef,$keynow);
			if($doi{$Account}){
				my $sql="REPLACE INTO ${PREF}doiaccounts (fk_doi,fk_account,fk_user) VALUES (?,?,?)";
				$db->do($sql,undef,$doikey,$_,$keynow);
				&Error;
#				insert_db("${PREF}doiaccounts",{fk_doi=>$doikey,fk_account=>$_,fk_user=>$keynow});
			}# if($doi{$Account})
		}#End foreach(@addaccount)
		if(@addaccount_unsubscribe){
			my $where_accounts=join(',',@addaccount_unsubscribe);
			my $sql="SELECT * FROM ${PREF}user WHERE fk_account IN ($where_accounts) AND email=?";
			my $out=$db->prepare($sql);
			$out->execute($Email);
			&Error($sql);
			while (my $user_info=$out->fetchrow_hashref){
				my $user_id=$user_info->{pk_user};
				doLog("Deleting $Name ($Email) from account $ACCOUNT{$user_info->{fk_account}}");
				DeleteUser($user_id);	
			}
		}
		if(@addaccount_suspend){
			my $where_accounts=join(',',@addaccount_suspend);
			my $sql="SELECT * FROM ${PREF}user WHERE fk_account IN ($where_accounts) AND email=?";
			my $out=$db->prepare($sql);
			$out->execute($Email);
			&Error($sql);
			while (my $user_info=$out->fetchrow_hashref){
				my $user_id=$user_info->{pk_user};
				doLog("Inactivating $Name ($Email) on account $ACCOUNT{$user_info->{fk_account}}");
				InactivateUser($user_id);	
			}
		}
		if(@addaccount_lock){
			my $where_accounts=join(',',@addaccount_lock);
			my $sql="SELECT * FROM ${PREF}user WHERE fk_account IN ($where_accounts) AND email=?";
			my $out=$db->prepare($sql);
			$out->execute($Email);
			&Error($sql);
			while (my $user_info=$out->fetchrow_hashref){
            my @chars=('a'..'z','A'..'Z',0..9,'_');
            my $ran=join("", @chars[map{rand @chars}(1..12)]);
            while(GetSQLCount("Select * from ${PREF}user WHERE unsubscribe=?",$ran)){
               $ran=join("", @chars[map{rand @chars}(1..12)]);
            }
            update_db("${PREF}user",{unsubscribe=>$ran},{pk_user=>$user_info->{pk_user}});
				my $user_id=$user_info->{pk_user};
				doLog("Locking $Name ($Email) on account $ACCOUNT{$user_info->{fk_account}}");
				InactivateUser($user_id);	
			}
		}

}else{
		#USER already exists
		my $u=select_one_db("SELECT * FROM ${PREF}user WHERE email=? AND fk_account=?",$Email,$Account);
		$USER_ID=$u->{pk_user};	
	}
	#End unless($count)
	return loaduser($USER_ID,undef,$Account);  
}
###
#sub LoadLinksInfo{
#	my $Account=shift;
#	my $sql=<<ALL__;
#SELECT * FROM ${PREF}links WHERE fk_account=? 
#ALL__
#	my $links={};
#	my $out=$db->prepare($sql);
#	$out->execute($Account);
#	while (%output=%{$out->fetchrow_hashref}){	
#		$links->{$output{pk_link}}={name=>$output{name},url=>}
#	}
#}
###
sub Broadcast{
	my $proc=shift;
	my $old_version=shift;
	local $db=&db_prepare;
	if($old_version){
		CanIWork($proc,0);
	}else{
		CanIWork($proc,1);
	}
	my $messcount=0;
	my %accountstat;
	my $messages_per_iteration=100;
	my %conf=loadCONF();
	my $sql=<<ALL__;
	SELECT pk_account,pk_mess,fk_user,${PREF}mess.typesend as typesend 
	FROM  ${PREF}account,${PREF}mess,${PREF}tosend 
	WHERE  ${PREF}tosend.fk_mess=${PREF}mess.pk_mess 
	AND ${PREF}tosend.proc=$proc
	AND ${PREF}account.pk_account=${PREF}mess.fk_account 
	ORDER BY pk_account ASC,pk_mess ASC
	LIMIT 0 , 100 
ALL__
	doMonitor($proc,"$LNG{BROADCAST_SENDER_PROCESS_STARTED}");
	my $oldaccount,$oldmess;
	my $mess,%conf,@FIELDS;	
	while(1){
		my $count;
		my $out=$db->prepare($sql);
		$out->execute();
		unless($out->rows){
			doMonitor($proc,"$LNG{BROADCAST_SENDER_PROCESS_FINISHED}");
			last;
		}
		my %output;
		while (%output=%{$out->fetchrow_hashref}){
			$count++;	
			if ($oldaccount!=$output{pk_account}){
				%conf=loadCONF($output{pk_account});
				@FIELDS=load_account_fields($output{pk_account});
				$oldaccount=$output{pk_account};
			}
			if ($oldmess!=$output{pk_mess}){
				$mess=load_mess($output{pk_mess});
				$oldmess=$output{pk_mess};
			}
			my $user=loaduser($output{fk_user},undef,$output{pk_account});
			my $messmime=GetMessForUser($user,\%conf,$mess,$output{pk_account});
			MIMEsendto($user->{email},$messmime);
			if ($mess->{typesend} =~ /unsubscribe/i){
				DeleteUser($user->{pk_user});	
			}
			$db->do("DELETE FROM ${PREF}tosend WHERE fk_user=? and fk_mess=?",undef,$output{fk_user},$output{pk_mess});
			$db->do("UPDATE ${PREF}mess SET sent=sent+1 WHERE pk_mess=?",undef,$output{pk_mess});
			$db->do("UPDATE ${PREF}user SET countsend=countsend+1 WHERE pk_user=?",undef,$output{fk_user});
			LogMessage($output{fk_user},$output{pk_mess},\%conf);
			if($conf{sendingdelay}){
				sleep($conf{sendingdelay});
				CanIWork($proc,0);
			}
		}
		doMonitor($proc,"$count $LNG{BROADCAST_MESSAGES_WAS_SENT1}. [" . GetSQLCount("SELECT * from ${PREF}tosend WHERE ${PREF}tosend.proc=$proc"). "] $LNG{BROADCAST_MESSAGES_WAS_SENT2}.");
		CanIWork($proc,0);
	}
}




###################
sub ErrorDBI{
	my $sql=shift;
	my $procno=shift;
	doMonitor($procno,"sql: $sql error: $DBI::err - $DBI::errstr") if $DBI::err;
}

# patch 001 changed redirect_link from varchar to text type
sub LoadUpdateStructure{
	###UPDATE INFO
		my @UPDATE=(
		{
			c=>sub{return 1 if GetSQLCount("SELECT * FROM ${PREF}mess where typesend = 'sent'")},
			v=>4.12,
			q=>"UPDATE ${PREF}mess SET typesend = 'manual' where typesend = 'sent'",
			n=>"Change type of manual messages"
		},
		{
			c=>sub{my %info=ColumnsInfo("${PREF}mess");return 1 if ($info{typesend}->{Type}=~/'sent'/);return 0;},
			v=>4.12,
			q=>"ALTER TABLE `${PREF}mess` CHANGE `typesend` `typesend` ENUM('manual','doi','auto','senddat','subscribe','unsubscribe') DEFAULT 'manual' NOT NULL ",
			n=>"Change message type structure"
		},	
		{
			c=>sub{return !IsColumnExists("${PREF}user",'ip')},
			v=>4.12,
			q=>"ALTER TABLE `${PREF}user` ADD `ip` VARCHAR(15)",
			n=>"Add IP logging for users"
		},
		
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'priority')},
			v=>4.14,
			q=>"ALTER TABLE `${PREF}mess` ADD `priority` INT",
			n=>"Add priority for messages"
		},	
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'encoding')},
			v=>4.14,
			q=>"ALTER TABLE `${PREF}mess` ADD `encoding` VARCHAR(15)",
			n=>"Add encoding for messages"
		},	
		{
			c=>sub{return !IsColumnExists("${PREF}user",'unsubscribe')},
			v=>4.14,
			q=>"ALTER TABLE `${PREF}user` ADD `unsubscribe` VARCHAR(12) BINARY",
			n=>"Add unsubscribe column for users"
		},	
		{
			c=>sub{return !IsIndexExists("${PREF}user",'unsubscribe')},
			v=>4.14,
			q=>"ALTER TABLE `${PREF}user` ADD INDEX (`unsubscribe`)",
			n=>"Create index to unsubscribe"
		},	
		{
			c=>sub{return !IsTableExists("${PREF}sentlog")},
			v=>4.14,
			q=>"CREATE TABLE `${PREF}sentlog` (`fk_user` INT NOT NULL, `fk_mess` INT NOT NULL, `date` DATETIME, PRIMARY KEY (`fk_user`,`fk_mess`))",
			n=>"Create table for messages log"
		},	
		{
			c=>sub{return !IsIndexExists("${PREF}sentlog",'PRIMARY') if IsTableExists("${PREF}sentlog")},
			v=>4.16,
			q=>"ALTER IGNORE TABLE `${PREF}sentlog` ADD PRIMARY KEY ( `fk_user` , `fk_mess` )",
			n=>"Create new index 'usermess' on ${PREF}sentlog"
		},
		{
			c=>sub{return !IsIndexExists("${PREF}fields",'fieldaddr')},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}fields` ADD INDEX `fieldaddr` ( `fieldname` , `fk_account` , `pk_fields` )",
			n=>"Add new index 'fieldaddr' on ${PREF}fields"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}tosend",'proc')},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}tosend` ADD `proc` TINYINT DEFAULT '0' NOT NULL",
			n=>"Add new 'proc' column to ${PREF}tosend"
		},	
		{
			c=>sub{return !IsColumnExists("${PREF}tosend",'paused')},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}tosend` ADD `paused` TINYINT DEFAULT '0' NOT NULL",
			n=>"Add new 'paused' column to ${PREF}tosend"
		},	
		{
			c=>sub{return !IsIndexExists("${PREF}tosend",'proc')},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}tosend` ADD INDEX ( `proc` )",
			n=>"Add new index 'proc' to ${PREF}tosend"
		},
		{
			c=>sub{return !IsIndexExists("${PREF}tosend",'procpaused')},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}tosend` ADD INDEX `procpaused` ( `proc` , `paused` )",
			n=>"Add new index 'procpaused' to ${PREF}tosend"
		},
		{
			c=>sub{my %info=IndexInfo("${PREF}user"); return 1 if exists($info{fk_account}{email}); return 0;},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}user` DROP INDEX `fk_account` ,ADD INDEX `fk_account` ( `fk_account` , `isact` )",
			n=>"Change index fk_account in table ${PREF}user"
		},	
		{
			c=>sub{return !IsTableExists("${PREF}brodcastlog")},
			v=>4.16,
			q=>"",
			s=>sub{
				my $sql="SELECT pk_mess, days FROM ${PREF}mess WHERE typesend='auto'";	
				my $out=$db->prepare($sql);
				$out->execute();
				&Error($sql);
				my $i=0;
				while (my $output=$out->fetchrow_hashref){
					$db->do("UPDATE ${PREF}user SET days=? WHERE messlastsend=?",undef,$output->{days}+1,$output->{pk_mess});
					&Error("UPDATE ${PREF}user SET days=$output->{days} WHERE messlastsend=$output->{pk_mess}");
				}			
			},
			n=>"Users database optimization"
		},
		{
			c=>sub{return !IsTableExists("${PREF}brodcastlog")},
			v=>4.16,
			q=>"CREATE TABLE `${PREF}brodcastlog` ( `pk_broadcastlog` int(11) default NULL auto_increment, `date` timestamp(14) ,  `procnomber` tinyint(4) NOT NULL default '0',  `pid` varchar(6) NOT NULL default '      ',  `log` text NOT NULL,  PRIMARY KEY (`pk_broadcastlog`),  KEY `procnomber`(`procnomber`)) TYPE=MyISAM",
			n=>"Add new table ${PREF}brodcastlog"
		},
		{
			c=>sub{return !IsTableExists("${PREF}stat_account_dayly")},
			v=>4.16,
			q=>"CREATE TABLE `${PREF}stat_account_dayly` (`fk_account` TINYINT NOT NULL ,`date` DATE NOT NULL ,`subscribers` INT NOT NULL DEFAULT 0,`unsubscribers` INT NOT NULL DEFAULT 0,`sent_manual` INT NOT NULL DEFAULT 0,`sent_sheduled` INT NOT NULL DEFAULT 0,`sent_sequential` INT NOT NULL DEFAULT 0,`sent_subscribe` INT NOT NULL DEFAULT 0,`sent_unsubscribe` INT NOT NULL DEFAULT 0,`sent_doubleoptin` INT NOT NULL DEFAULT 0,PRIMARY KEY ( `fk_account` , `date` ) )",
			n=>"Add new table ${PREF}stat_account_dayly"
		},	
		{
			c=>sub{return !IsTableExists("${PREF}stat_dayly")},
			v=>4.16,
			q=>"CREATE TABLE `${PREF}stat_dayly` (`date` DATE NOT NULL ,`broadcast_starts` INT NOT NULL DEFAULT 0 , is_adm_notif TINYINT NOT NULL DEFAULT 0,PRIMARY KEY ( `date` ) )",
			n=>"Add new table ${PREF}stat_dayly"
		},
		{
			c=>sub{return !IsTableExists("${PREF}process_loc")},
			v=>4.16,
			q=>"CREATE TABLE `${PREF}process_loc` (  `pk_process_loc` int(11) NOT NULL  auto_increment,  `date` datetime NOT NULL default '0000-00-00 00:00:00',  `PID` varchar(8) NOT NULL default '',  `procnomber` tinyint(4) NOT NULL default '0',  PRIMARY KEY (`pk_process_loc`),  KEY `procnomber`(`procnomber`)) TYPE=MyISAM",
			n=>"Add new table ${PREF}process_loc"
		}, 
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'issendnow')},
			v=>4.16,
			q=>"ALTER TABLE `${PREF}mess` ADD `issendnow` TINYINT DEFAULT '0' NOT NULL",
			n=>"Add new 'issendnow' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsTableExists("${PREF}links")},
			v=>4.18,
			q=>"CREATE TABLE `${PREF}links` (`pk_link` INT NOT NULL AUTO_INCREMENT ,`name` VARCHAR( 100 ) NOT NULL ,`redirect_link` TEXT NOT NULL ,`fk_account` INT NOT NULL ,PRIMARY KEY ( `pk_link` ) ,INDEX ( `fk_account` ) ) TYPE=MyISAM",
			n=>"Add new table ${PREF}links"
		},
		{
			c=>sub{return !IsTableExists("${PREF}link_clicks")},
			v=>4.18,
			q=>"CREATE TABLE 
			${PREF}link_clicks (  
			pk_link_click int(11) default NULL auto_increment,  
			fk_link int(11) default '0',  
			fk_user int(11) default '0',  
			fk_mess int(11) default '0',  
			timestamp timestamp(14) ,  
			PRIMARY KEY (pk_link_click),  
			KEY fk_account(fk_user,fk_mess,fk_link),  KEY timestamp(timestamp)) TYPE=MyISAM",
			n=>"Add new table ${PREF}link_clicks"
		},
		{
			c=>sub{return !IsTableExists("${PREF}bounce_account")},
			v=>4.19,
			q=>"CREATE TABLE `${PREF}bounce_account` (
			  `pk_bounce_account` int(11) default NULL auto_increment,
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
			  ) TYPE=MyISAM",
			n=>"Add new table ${PREF}bounce_account"
		},
		{
			c=>sub{return !IsTableExists("${PREF}bounce_allmessages")},
			v=>4.19,
			q=>"CREATE TABLE `${PREF}bounce_allmessages` (
			  `messageid` varchar(150) NOT NULL default '',
			  `date` datetime,
			  PRIMARY KEY (`messageid`)
			  ) TYPE=MyISAM",
			n=>"Add new table ${PREF}bounce_allmessages"
		},
		{
			c=>sub{return !IsTableExists("${PREF}bounce_banemails")},
			v=>4.19,
			q=>"CREATE TABLE `${PREF}bounce_banemails` (
			  `email` varchar(150) NOT NULL default '',
			  PRIMARY KEY (`email`)
			  ) TYPE=MyISAM",
			n=>"Add new table ${PREF}bounce_banemails"
		},
		{
			c=>sub{return !IsTableExists("${PREF}bounce_messages")},
			v=>4.19,
			q=>"CREATE TABLE `${PREF}bounce_messages` (
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
			  ) TYPE=MyISAM",
			n=>"Add new table ${PREF}bounce_messages"
		},
		{
			c=>sub{my %info=ColumnsInfo("${PREF}user"); return($info{days}->{Type}=~/tinyint/i)},
			v=>4.19,
			q=>"ALTER TABLE `${PREF}user` CHANGE `days` `days` INT DEFAULT '0'",
			s=>sub{
				my $sql="SELECT pk_mess, days FROM ${PREF}mess WHERE typesend='auto'";	
				my $out=$db->prepare($sql);
				$out->execute();
				&Error($sql);
				my $i=0;
				while (my $output=$out->fetchrow_hashref){
					$db->do("UPDATE ${PREF}user SET days=? WHERE messlastsend=?",undef,$output->{days}+1,$output->{pk_mess});
					&Error("UPDATE ${PREF}user SET days=$output->{days} WHERE messlastsend=$output->{pk_mess}");
				}			
			},
			n=>"Change type of '<B><i>day</i></B>' column to INT in the <B>${PREF}user</B> table.<BR> BUG with more then 127 days sequence. Fixing sequence."
		},
		{
			c=>sub{my %info=ColumnsInfo("${PREF}account"); return($info{name}->{Type}=~/16/i)},
			v=>4.19,
			q=>"ALTER TABLE `${PREF}account` CHANGE `name` `name` VARCHAR(30) NOT NULL",
			n=>"Increase length of the account name"
		},
		{
			c=>sub{my %info=ColumnsInfo("${PREF}mess"); return $info{type}->{Type}!~/mixed/},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}mess` CHANGE `type` `type` ENUM( 'text', 'html', 'mixed' ) DEFAULT 'text' NOT NULL",
			n=>"Adding 'HTML and text' type of messages"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'messhtml')},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}mess` ADD `messhtml` TEXT AFTER `mess`",
			s=>sub{
				$db->do("UPDATE ${PREF}mess SET messhtml=mess");
				$db->do("UPDATE ${PREF}mess SET messhtml='' WHERE type='text'");
				$db->do("UPDATE ${PREF}mess SET mess='' WHERE type='html'");
			},
			n=>"Add new 'messhtml' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'defmesstype')},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}mess` ADD `defmesstype` TINYINT DEFAULT '1' AFTER `type`",
			n=>"Add new 'defmesstype' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'saveinhistory')},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}mess` ADD `saveinhistory` VARCHAR(2)",
			n=>"Add new 'saveinhistory' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'messrss')},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}mess` ADD `messrss` TEXT",
			n=>"Add new 'messrss' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'rsslink')},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}mess` ADD `rsslink` TEXT",
			n=>"Add new 'rsslink' column to ${PREF}mess"
		},		
		{
			c=>sub{return !IsColumnExists("${PREF}user",'messageformat')},
			v=>4.21,
			q=>"ALTER TABLE `${PREF}user` ADD `messageformat` TINYINT DEFAULT '0' NOT NULL",
			n=>"Add new 'defmesstype' column to ${PREF}user"
		},
		{
			c=>sub{return !IsTableExists("${PREF}senthistory")},
			v=>4.21,
			q=>"CREATE TABLE `${PREF}senthistory` (`fk_user` INT NOT NULL, `fk_mess` INT NOT NULL, `date` DATETIME, PRIMARY KEY (`fk_user`,`fk_mess`))",
			n=>"Create new table '${PREF}senthistory' for messages sent history"
		},
		{
			c=>sub{return !IsTableExists("${PREF}changepref")},
			v=>4.21,
			q=>"CREATE TABLE `${PREF}changepref` (  `pk_changepref` int(11)  auto_increment,  `fk_user` int(11) NOT NULL default '0',  `ran` varchar(15) NOT NULL default '',  `name` varchar(60) NOT NULL default '',  `email` varchar(120) NOT NULL default '',  `ip` varchar(15) default NULL,  `messageformat` tinyint(4) NOT NULL default '0',  `date` timestamp(14) ,  PRIMARY KEY (`pk_changepref`)) TYPE=MyISAM",
			n=>"Create new table '${PREF}changepref'"
		},
		{
			c=>sub{return !IsTableExists("${PREF}signatures")},
			v=>5.01,
			q=>"CREATE TABLE `${PREF}signatures` (`pk_signature` INT NOT NULL AUTO_INCREMENT PRIMARY KEY ,`name` VARCHAR( 15 ) NOT NULL ,`sig_text` TEXT NULL ,`sig_html` TEXT NULL ,UNIQUE (`name` )) TYPE=MyISAM",
			n=>"Create new table '${PREF}signatures'"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}user",'fk_affiliate')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` ADD `fk_affiliate` INT NULL",
			n=>"Add new 'fk_affiliate' column to ${PREF}user"
		},
		{
			c=>sub{return !IsIndexExists("${PREF}user",'fk_affiliate')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` ADD INDEX ( `fk_affiliate` ) ",
			n=>"Add new index 'fk_affiliate' to ${PREF}user"
		},
		{
			c=>sub{return IsIndexExists("${PREF}user",'actaccountdays')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` DROP INDEX `actaccountdays`",
			n=>"Delete index 'actaccountdays' in ${PREF}user"
		},
		{
			c=>sub{return IsIndexExists("${PREF}user",'sequential')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` DROP INDEX `sequential`",
			n=>"Delete index 'sequential' in ${PREF}user"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}user",'fromname')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` ADD `fromname` VARCHAR( 80 ) NULL ",
			n=>"Add new 'fromname' column to ${PREF}user"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}user",'referrer_link')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` ADD `referrer_link` VARCHAR( 12 ) NULL",
			n=>"Add new 'referrer_link' column to ${PREF}user"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}user",'sequence_repeat')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` ADD `sequence_repeat` INT NOT NULL DEFAULT '0'",
			n=>"Add new 'sequence_repeat' column to ${PREF}user"
		},		
		{
			c=>sub{return !IsColumnExists("${PREF}user",'fromemail')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}user` ADD `fromemail` VARCHAR( 80 ) NULL ",
			n=>"Add new 'fromemail' column to ${PREF}user"
		},		
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'fromnamemess')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}mess` ADD `fromnamemess` VARCHAR( 80 ) NULL",
			n=>"Add new 'fromnamemess' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'fromemailmess')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}mess` ADD `fromemailmess` VARCHAR( 80 ) NULL",
			n=>"Add new 'fromemailmess' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'usefrom')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}mess` ADD `usefrom` TINYINT NULL DEFAULT '0'",
			n=>"Add new 'usefrom' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}mess",'repeating')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}mess` ADD `repeating` TINYINT NULL DEFAULT '0'",
			n=>"Add new 'repeating' column to ${PREF}mess"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}account",'descr')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}account` ADD `descr` VARCHAR( 150 ) NULL",
			n=>"Add new 'descr' column to ${PREF}account"
		},
		{
			c=>sub{return !IsColumnExists("${PREF}account",'position')},
			v=>5.01,
			q=>"ALTER TABLE `${PREF}account` ADD `position` INT DEFAULT '0' NOT NULL",
			n=>"Add new 'position' column to ${PREF}account"
		}
	);
	return @UPDATE;
}

sub LoadAccountSequence{
	my $account=shift;
	return(@{$CASH_SEQUENSE{$account}}) if(exists($CASH_SEQUENSE{$account}));
		
	my $sql="select pk_mess,days from ${PREF}mess WHERE fk_account=? AND typesend='auto' ORDER BY days ASC";
	my $out=$db->prepare($sql);
	$out->execute($account);
	my $prev_days=0;
	my @seq=();
	while (my $mess=$out->fetchrow_hashref){
		push(@seq,{pk_mess=>$mess->{pk_mess},days=>$mess->{days}});		
	}
	$CASH_SEQUENSE{$account}=\@seq;
	return @seq;
}

sub GetSQLWhereRulesArray{
	return('=','>','<','>=', '<=','like','not like', 'is null','is not null');
}
sub GetSQLWhereRules{
	my $r;
	map {$r->{$_}=1}('=','>','<','>=', '<=','like','not like', 'is null','is not null');
	return $r;
}
###END UPDATE INFO
sub AccountUsersSQL{
	my $fk_account=shift;
	my $where=shift;
	my $order=shift;
	my $affiliate_levels=shift;
	my $is_count_query=shift;
	#$affiliate_levels=5 unless defined $affiliate_levels;
	my %as_fileds=(); 
	unless(%CASH_USER_TABLE_FILEDS){
		%CASH_USER_TABLE_FILEDS=ColumnsInfo("${PREF}user");	
	}
	map{$as_fileds{$_}="${PREF}user.$_"}keys %CASH_USER_TABLE_FILEDS;
	#$order={email=>"asc", name=>'desc' };
	push(@$where,["fk_account",'=',$fk_account]);
	my @fields=load_account_fields($fk_account);
	my @seq=LoadAccountSequence($fk_account);
	my $sequence_now;
	if(@seq){
		$sequence_now="CASE ${PREF}user.messlastsend ";
		my $i;
		foreach(@seq){
			$i++;
			$sequence_now.=" WHEN $_->{pk_mess} THEN $i ";
		}
		$sequence_now.=" ELSE 0 END ";
		

	}else{
		$sequence_now="0" 
	}
	$as_fileds{sequence_now}=$sequence_now;
	$sequence_now.=" AS sequence_now";
	my $Inactive=$db->quote($LNG{USR_BROWSER_INACTIVE});
	my $Active=$db->quote($LNG{USR_BROWSER_ACTIVE});
	my $Pending=$db->quote($LNG{USR_BROWSER_PENDING});
	my $Status_query=" if(${PREF}user.isact=0, if( ${PREF}doiaccounts.fk_doi IS NULL , $Inactive, $Pending ), $Active) ";
	
	my @sql_fields=(
		"`${PREF}user`.*, UNIX_TIMESTAMP(`${PREF}user`.datereg) AS unixregdate",
		scalar(@seq)." AS sequense_size", 
		$sequence_now, 
		"$Status_query as status",
	       "CASE ${PREF}user.messageformat WHEN 1 THEN ".$db->quote($LNG{USR_BROWSER_TEXT_USER_FORMAT})." WHEN 2 THEN ".$db->quote($LNG{USR_BROWSER_HTML_USER_FORMAT})." ELSE ".$db->quote($LNG{USR_BROWSER_DEFAULT_FORMAT})." END AS usermessageformat"	
	);
	$as_fileds{status}=$Status_query;
	$as_fileds{sequense_size}=scalar(@seq);
	map{
		push(@sql_fields,"parentaffiliate".$_.".pk_user AS affiliate".$_."id");
		$as_fileds{"affiliate".$_."id"}="parentaffiliate".$_.".pk_user";
		push(@sql_fields,"parentaffiliate".$_.".name AS affiliate".$_."name");
		$as_fileds{"affiliate".$_."name"}="parentaffiliate".$_.".name";		
		push(@sql_fields,"parentaffiliate".$_.".email AS affiliate".$_."email");
		$as_fileds{"affiliate".$_."email"}="parentaffiliate".$_.".email";		
	}(1..$affiliate_levels);
	map{
		push(@sql_fields,"${PREF}doppar$_->{key}.value AS field$_->{key}");
		$as_fileds{"field$_->{key}"}="${PREF}doppar$_->{key}.value";
	}@fields;
	if($is_count_query){
		@sql_fields=("count(*) as count");
	}
	my $sql_fields=join(', ',@sql_fields);
	my @sql_join=();
	map{push(@sql_join,"LEFT JOIN `${PREF}doppar` AS `${PREF}doppar$_->{key}` ON `${PREF}doppar$_->{key}`.fk_fields =$_->{key} AND `${PREF}user`.pk_user = `${PREF}doppar$_->{key}`.fk_user")}@fields;
	push(@sql_join,"LEFT JOIN ${PREF}doiaccounts ON ${PREF}doiaccounts.fk_user = ${PREF}user.pk_user");
	map{
		if($_==1){
			push(@sql_join,"LEFT JOIN ${PREF}user as parentaffiliate1 ON parentaffiliate1.pk_user = ${PREF}user.fk_affiliate");
		}else{
			my $prev=$_-1;
			my $now=$_;
			push(@sql_join,"LEFT JOIN ${PREF}user as parentaffiliate$now ON parentaffiliate$now.pk_user = parentaffiliate$prev.fk_affiliate");
		}
	}(1..$affiliate_levels);	
	my $sql_join=join("\n",@sql_join);
	my @where=();
	map{
		my $rules=GetSQLWhereRules();
		my $rule=$_->[1] if exists($rules->{$_->[1]});
		$rule='like' unless exists($rules->{$_->[1]});
		my $value=$_->[2];
		my $fieldnow=$_->[0];
		if (exists ($as_fileds{$fieldnow})){
			if($rule=~/=|>|</){
				if($value=~/^-?[0-9]$/){
					push(@where,"$as_fileds{$fieldnow} $rule $value");
				}elsif(length($value)){
					push(@where,"$as_fileds{$fieldnow} $rule ".$db->quote($value));	
				}else{
					push(@where,"$as_fileds{$fieldnow} $rule NULL");
				}
			}elsif($rule=~/like/i){
				push(@where,"$as_fileds{$fieldnow} ".uc($rule).'('.$db->quote('%'.$value.'%').")");				
			}else{
				push(@where,"$as_fileds{$fieldnow} ".uc($rule));
			}
		}
	}@$where;
	my $where_sql=join(" AND ",@where);	
	my $order_sql=join (", ",map{"`$_` $order->{$_}"}keys %$order);
	$order_sql="ORDER BY ".$order_sql if length($order_sql);
	my $sql=<<ALL__;
SELECT  $sql_fields
FROM `${PREF}user` 
$sql_join
WHERE $where_sql
$order_sql
ALL__
return $sql;
}
sub GetAllAccountFields{
	my $fk_account=shift;
	my $affiliate_levels=shift;
	my $active_fields_now=shift;
	my %from_conf=();
	map{$from_conf{$_}=1}split(/\t/,$active_fields_now);
#	die join '|', keys %from_conf;
	my %fields_descr=();
	my @user_table_fields=qw(pk_user datereg days datelastsend messlastsend countsend ip unsubscribe sequence_now sequense_size sequence_repeat status fromemail fromname usermessageformat referrer_link);
	map{$fields_descr{$_}=$LNG{"FLD_".uc($_)}}@user_table_fields;
	my @add_fields=load_account_fields($fk_account);
	map{
		push(@user_table_fields,"field$_->{key}");
		$fields_descr{"field$_->{key}"}=$_->{name}
	}@add_fields;
	if($affiliate_levels){
		map{
			push(@user_table_fields,"affiliate".$_."id");
			push(@user_table_fields,"affiliate".$_."name");
			push(@user_table_fields,"affiliate".$_."email");
			my $lev="";
			$lev=$_ if ($_>1);
			$fields_descr{"affiliate".$_."id"} = "$LNG{PARENT_AFFILIATE} $lev $LNG{FLD_KEY}";
			$fields_descr{"affiliate".$_."name"} = "$LNG{PARENT_AFFILIATE} $lev $LNG{FLD_NAME}";
			$fields_descr{"affiliate".$_."email"} = "$LNG{PARENT_AFFILIATE} $lev $LNG{FLD_EMAIL}";			
		}(1..$affiliate_levels);
	}
	my @fields_now=();
	my @not_selected=();

	$from_conf{$active_fields_now}=1;


	map{
		push(@fields_now,$_) if exists $from_conf{$_};
		push(@not_selected,$_) unless exists $from_conf{$_};		
	}@user_table_fields;
	return {
		allfields=>\@user_table_fields,
		names=>\%fields_descr,
		selected_fields=>\@fields_now,
		avalible_fields=>\@not_selected
	};
}
sub GetStatDailyPage{
	my $br_log=select_one_db("SELECT *,UNIX_TIMESTAMP(date) AS unixdate FROM ${PREF}stat_dayly WHERE date = CURDATE() - INTERVAL 1 DAY");
	my %conf=loadCONF();
	open(FILE , "shabl/daylystat.html")|| return;
	local $/ = undef;
	my $html = <FILE>;
	close(FILE);
	$html=~s/<!--hide-->.*?<!--endhide-->//gis;
	open(FILE , "shabl/style.css")|| return;
	my $css = <FILE>;
	$html=~s/{CSS}/$css/gis;
	close(FILE);	
	my $br_starts=$br_log->{broadcast_starts}||0;
	$html=~s/\{BR_STARTS\}/ $br_starts /gs;
	my $sent_log,$account_log,$subscribers_log;
	my $report_date=strftime($conf{date_format}||'%m/%d/%Y', localtime($MY_TIME - 24*60*60));
	$html=~s/###TITLE###/$LNG{DAILY_REPORT}: $report_date/gs;
	my $timesent=localtime($MY_TIME);
	$html=~s/\{DATE_NOW\}/$timesent/gs;
	#LANG 
	$html=~s/\[LNG_BRODC_STARTED\]/$LNG{BRODC_STARTED}/gs;
	$html=~s/\[LNG_TIMES_THIS_DAY\]/$LNG{TIMES_THIS_DAY}/gs;
	$html=~s/\[LNG_REPORT_GEN\]/$LNG{REPORT_GEN}/gs;
	###ACCOUNT
	my $sql="select * from ${PREF}account";
	my $out=$db->prepare($sql);
	$out->execute();
	my %accountname;
	while (my %output=%{$out->fetchrow_hashref}){
		$accountname{$output{pk_account}}=$output{name};
	}
	my $Total_act,$Total_inact;
my $account_log=<<ALL__;
<h2>$LNG{ACCOUNTS_PROSPECTS}</h2>
<table border="0" align="center" width="50%" cellspacing="1" cellpadding="2">
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
		$account_log.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left">$accountname{$account_id}</td>
 <td >$total_activ</td>
 <td >$total_inactiv</td>
 <td >$total</td>
</tr>	
ALL__
		
	}
	my $tot=$Total_inact+$Total_act;
	$account_log.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><b>$LNG{STAT_TOTAL}:</b></td>
 <td ><b>$Total_act</b></td>
 <td ><b>$Total_inact</b></td>
 <td ><b>$tot</b></td>
</tr>	
</table>
ALL__
###SUBSCRIBERS
	my $sql=<<ALL__;
SELECT  `name`,`pk_account` ,    
SUM(`subscribers`) as subscribers ,  
SUM(`unsubscribers`) as unsubscribers,
SUM(`subscribers`)-SUM(`unsubscribers`) as  total_subscribers
FROM  `${PREF}stat_account_dayly` 
RIGHT JOIN ${PREF}account ON pk_account=fk_account
WHERE date='$br_log->{date}'
GROUP BY fk_account
HAVING subscribers<>0 OR unsubscribers<>0 ORDER by total_subscribers DESC
ALL__

	my $out=$db->prepare($sql);
	$out->execute();
	unless ($out->rows()){
		$subscribers_log.=<<ALL__;
		<H2>$LNG{NO_SUBS_OR_UNSUBS_THIS_DATE}</H2>
ALL__
	}else{	
		$subscribers_log.=<<ALL__;
 <h2>$LNG{STAT_SUBSCRIBERS}/$LNG{STAT_UNSUBSCRIBERS}</h2>
<table border="0" align="center" width="50%" cellspacing="1" cellpadding="2">
<tr class="dataheader"> 
 <td >$LNG{STAT_ACCOUNT}</td>
 <td >$LNG{STAT_SUBSCRIBERS}</td>
 <td >$LNG{STAT_UNSUBSCRIBERS}</td>
 <td >$LNG{STAT_TOTAL}</td>
</tr>
ALL__
		my %itog;
		while (my $output=$out->fetchrow_hashref){
			map{$itog{$_}=$itog{$_}+$output->{$_} unless(/account|name/)}keys %{$output};
			$subscribers_log.=<<ALL__;
<tr class="data" align="right"> 
 <td align="left">$output->{name}</td>
 <td >$output->{subscribers}</td>
 <td >$output->{unsubscribers}</td>
 <td >$output->{total_subscribers}</td>
</tr>
ALL__
		}
		$subscribers_log.=<<ALL__;
 <tr class="data" align="right"> 
 <td align="left"><b>$LNG{STAT_TOTAL}</b></td>
 <td ><b>$itog{subscribers}</b></td>
 <td ><b>$itog{unsubscribers}</b></td>
 <td ><b>$itog{total_subscribers}</b></td>
</tr>	
</table>
ALL__
	}	
###SENT MESSAGES	
	my $sql=<<ALL__;
SELECT  `name`,`pk_account` ,    
SUM(`sent_manual`) as `sent_manual`,
SUM(`sent_sheduled`) as `sent_sheduled`,
SUM(`sent_sequential`) as `sent_sequential` ,
SUM(`sent_subscribe`) as `sent_subscribe`,
SUM(`sent_unsubscribe`) as `sent_unsubscribe` ,
SUM(`sent_doubleoptin`) as `sent_doubleoptin` ,
SUM(`sent_manual`)+SUM(`sent_sheduled`)+SUM(`sent_sequential`)+SUM(`sent_subscribe`)+SUM(`sent_unsubscribe`) as total_sent
FROM  `${PREF}stat_account_dayly` 
RIGHT JOIN ${PREF}account ON pk_account=fk_account
WHERE date='$br_log->{date}'
GROUP BY fk_account
HAVING total_sent<>0 ORDER by total_sent DESC 
ALL__
	my $out=$db->prepare($sql);
	$out->execute();
	unless ($out->rows()){
		$sent_log.=<<ALL__;
		<H2>$LNG{STAT_NO_MESS}</H2>
ALL__
	}else{	
		$sent_log.=<<ALL__;
<h2>$LNG{USR_SENT_MESS}</h2>
<table border="0" align="center" width="90%" cellspacing="1" cellpadding="2">
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
		my %itog;
		while (my $output=$out->fetchrow_hashref){
			map{$itog{$_}=$itog{$_}+$output->{$_} unless(/account|name/)}keys %{$output};
			$sent_log.=<<ALL__;
<tr class="data" align="right"> 
 <td align="left">$output->{name}</td>
 <td >$output->{sent_sequential}</td>
 <td >$output->{sent_sheduled}</td>
 <td >$output->{sent_manual}</td>
 <td >$output->{sent_doubleoptin}</td>
 <td >$output->{sent_subscribe}</td>
 <td >$output->{sent_unsubscribe}</td>
 <td >$output->{total_sent}</td>
</tr>
ALL__
		}
		$sent_log.=<<ALL__;
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
	}	
###SENT MESSAGES
#	my $sent_log,$account_log,$subscribers_log;
	$html=~s/###SENT_LOG###/$sent_log/gs;
	$html=~s/###ACCOUNT_LOG###/$account_log/gs;
	$html=~s/###SUBSCRIBERS_LOG###/$subscribers_log/gs;
	$html=~s/{YEAR_NOW}/$YEAR_NOW/gs;
	
return $html;

}
sub guestip{
        my($visitor,$userip);
        for $visitor ($ENV{REMOTE_ADDR},
                $ENV{HTTP_VIA},
                $ENV{HTTP_X_FORWARDED_FOR}) {
                if ($visitor=~/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/){
                        return($1,$2,$3,$4);
                }
        };
        return (0,0,0,0);
}
sub is_ip_banned{
        my @ip=guestip(); return 0 unless (scalar(@ip)==4);
        my $IPBASE=loadIPbase($CONF{ipbanlist});
        if($IPBASE->{$ip[0]}{$ip[1]}{$ip[2]}{$ip[3]}[0]){
	print "Content-Type: text/html; charset=ISO-8859-1\n\n";
	print <<ALL__;
<html>
<head>
	<title>$CONF{ipbanlist_error}</title>
</head>
<BODY>
<h1 align="center"><font color="red">$CONF{ipbanlist_error}</FONT></H1>
</BODY>
ALL__
		exit;
        }
}
sub loadIPbase{
	my $TEXT=shift;
        my $IPBASE_REF;
	my @lines=split(/\n/,$TEXT);
        foreach(@lines){
                chomp;
                s/#(.*)$//;
                my $robotdiscr=$1;
                s/\s+//g;
                if (/([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9*-]{1,7})/){
                        my ($ip1,$ip2,$ip3,$ip4)=($1,$2,$3,$4);
                        my @iprange=();
                        if($ip4=~/-/){
                                ($ip4_1,$ip4_2)=split(/-/,$ip4);
                                for (my $i=int($ip4_1);$i<=int($ip4_2);$i++){
                                        push(@iprange,$i)
                                }
                        }elsif($ip4=~/\*/){
                                @iprange=(0..254);
                        }else{
                                push(@iprange,$ip4);
                        }
                        foreach my $ip4 (@iprange){
                                $IPBASE_REF->{int($ip1)}{int($ip2)}{int($ip3)}{int($ip4)}=[1,$robotdiscr];
                        }
                }

        }
        close(FILE);
        return $IPBASE_REF;
}

1;
