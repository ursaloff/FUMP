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
if($PAR{id}){
	$PAR{id}=unfsmy($PAR{id});
	($PAR{u},$PAR{id})=split(/hBdLktUuSp/,$PAR{id});
}
unless(length $PAR{u}){
	print_error("Incorrect request");
}
my $user=select_one_db("SELECT *, UNIX_TIMESTAMP(datereg) AS unixregdate FROM ${PREF}user WHERE unsubscribe=?",$PAR{u});
print_error("Sorry, but subscriber was not found") unless($user->{pk_user});
%CONF=loadCONF($user->{fk_account});
if($PAR{id}){
	printMess($user,\%CONF,$PAR{id});
	
}
unless($PAR{m} eq 'web' ){
	printRSS($user,\%CONF);
}else{
	printWEB($user,\%CONF);
}
sub printMess{
	my $user=shift;
	my $conf=shift;
	my $mess_id=shift;
	my $mess=load_mess($mess_id);
	my $messtext=GetMessText($user,$conf,$mess,$user->{fk_account},1);
	$messtext   =PersonalizeText($messtext   ,$conf,$user,$mess);
	my $messsubject=$mess->{subject};
	$messsubject=PersonalizeText($messsubject,$conf,$user,$mess);
	printheader();
	if($mess->{type}=~/html/i){
		print $messtext;
		exit;
	}else{
		eval{
			use HTML::TextToHTML;
			my $conv = new HTML::TextToHTML();
			print $q->start_html($messsubject);
			print  $conv->process_chunk($messtext);
			print $q->end_html;
		};			
	}
	exit;
}
sub printWEB{
	my $user=shift;
	my $conf=shift;
	my $page = new repparser(
		IS_CRIPT=>0,
		DATA=>"$SHABL_DIR/history.html",
		ERROR_AFTER_INPUT=>1
	);
	my $sql="SELECT fk_user, fk_mess, UNIX_TIMESTAMP(date) AS date, pk_mess, subject, messrss FROM ${PREF}senthistory LEFT JOIN ${PREF}mess ON pk_mess=fk_mess WHERE fk_user=? and pk_mess IS NOT NULL ORDER BY date DESC";
	my $out=$db->prepare($sql);
	$out->execute($user->{pk_user});
	while (my $output=$out->fetchrow_hashref){
		unless($conf->{date_format}){
			$conf->{date_format}='%m/%d/%Y';
		}
		my $rss_mess=$output->{messrss};
		eval{
		 use HTML::TextToHTML;
		 my $conv = new HTML::TextToHTML();
		 $rss_mess = $conv->process_chunk(PersonalizeText($rss_mess,$conf,$user));
		};
		$output->{messrss}=$rss_mess;
		$unicid=create_id("$PAR{u}hBdLktUuSp$output->{fk_mess}");
		#$output->{visit_link_download}="$ENV{SCRIPT_NAME}?id=$unicid&act=d";
		#$output->{visit_link}="$ENV{SCRIPT_NAME}?id=$unicid";
		$output->{visit_link}="$conf->{serverurl}rss.cgi?id=$unicid";
		$output->{date}=strftime($conf->{date_format},localtime($output->{date}));
		$page->AddRow($output);
	}
	$page->ParseData;
	my $output=$page->as_string;
	$output=PersonalizeText($output,$conf,$user);
	printheader();
	print $output;
	#print_error('WEB');	
}
sub create_id{
	my $what=shift;
	$what=~s/([^a-zA-Z0-9\t :,#<>@])/"_".sprintf("%02x",ord($1))/ge;
	$what=~tr/DNfeQS5Ouj6rMkIg9PwTXHzC1Vc3vEA8nxlLF7KYbsUmJhZ4WoRqiGpy0aBd2t/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/;
	return $what;
}
#sub prepare_rss_date{
#	my $time=shift;
#	#Thu, 23 Aug 1999 07:00:00 GMT
#	strftime("");
#}
sub printRSS{
	my $user=shift;
	my $conf=shift;
	eval( 'use XML::RSS');
	die "Can not load XML::RSS module:$@" if $@;
	my $rss = new XML::RSS (version => '2.0');
 	$rss->channel(
		title	=> $conf->{rss_title},
		link	=> $conf->{rss_link},
		language=> $conf->{rss_lang},
		description	=> $conf->{rss_description},
		copyright      => $conf->{rss_copy_line},
		pubDate        => scalar(localtime($user->{unixregdate})),
		managingEditor => $conf->{fromemail},
		webMaster      => $conf->{fromemail}
               );
	my $sql="SELECT fk_user, fk_mess, UNIX_TIMESTAMP(date) AS date, pk_mess, subject, messrss FROM ${PREF}senthistory LEFT JOIN ${PREF}mess ON pk_mess=fk_mess WHERE fk_user=? and pk_mess IS NOT NULL ORDER BY date ASC";
	my $out=$db->prepare($sql);
	$out->execute($user->{pk_user});
	my $lastdate;
	while (my $output=$out->fetchrow_hashref){
		unless($conf->{date_format}){
			$conf->{date_format}='%m/%d/%Y';
		}
		$lastdate=$output->{date};
		my $rss_mess=$output->{messrss};
		$rss_mess=~s/\n/<BR>\n/gs;
		$output->{messrss}=$rss_mess;
		$unicid=create_id("$PAR{u}hBdLktUuSp$output->{fk_mess}");
		$output->{visit_link}="$conf->{serverurl}rss.cgi?id=$unicid";
		$output->{date}=strftime($conf->{date_format},localtime($output->{date}));
		#$page->AddRow($output);
		$rss->add_item(
			title       => PersonalizeText("$output->{date} $output->{subject}",$conf,$user),
			link        => $output->{visit_link},
			description => PersonalizeText($rss_mess,$conf,$user)
		);
	}
 	$rss->channel(lastBuildDate  => scalar(localtime($lastdate)));

	if($conf->{rss_use_text_input}){
		$rss->textinput(
			title => $conf->{rss_ti_title},
			description => $conf->{ti_description},
			name  => $conf->{rss_ti_name},
			link  => $conf->{rss_ti_link}
		);
	}
	print $q->header(-type=>'text/xml',	-charset=>$conf->{rss_encoding});
	print $rss->as_string;
	exit;

}
#map{$page->set_def($_,$user->{$_})}qw(name email messageformat);
#map{$page->set_input($_,{size=>30})}qw(name email);
#$page->add_element('messageformat',1,$LNG{TEXT_ONLY});
#$page->add_element('messageformat',2,$LNG{HTML_ONLY});
#$page->Hide('<!--SECOND_STEP-->');
#$page->Hide('<!--THIRD_STEP-->');



sub print_error{
	my $mess=shift;
	printheader();
	print $q->start_html($mess);
	print qq|<h1 align="center"><font color="red">$mess</font></h1>|;
	print $q->end_html();
	exit();
}
