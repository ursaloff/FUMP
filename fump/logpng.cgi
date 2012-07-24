#!/usr/bin/perl
######################################################################
# Follow Up Mailing List Processor                                   #
# Version 5.01                                                       #
# Last modified 08/29/2006                                           #
######################################################################
use lib('lib');
#use CGI::Carp qw(fatalsToBrowser);
eval("use GD::Graph::bars;use GD::Graph::hbars;use GD::Graph::Data;");
if ($@){
&printError;
}
sub printError{
	binmode(STDOUT);
	print "Content-Type: image/gif\n\n";
	open (FILE,"shabl/img/errorgd.gif");
	binmode(FILE);
	$/=undef;
	my $data=<FILE>;
	print $data;
	exit;
}
sub printEmpty{
	binmode(STDOUT);
	print "Content-Type: image/gif\n\n";
	map{print chr($_)}qw(71 73 70 56 57 97 2 0 2 0 128 1 0 153 153 153 255 255 255 33 249 4 1 0 0 1 0 44 0 0 0 0 2 0 2 0 0 2 2 140 83 0 59);
	exit;
}
require "conf.cgi";
#use resplogdata;
local @DEF_BLOKS=(
		y_tick_number       => 10,
		y_label_skip        => 2,
		long_ticks          => 1,
		two_axes            => 0,
		legend_placement    => 'BC',
		x_label_position    => 1/2,
		bgclr		    => 'white',
	       	fgclr               => 'white',
		boxclr              => '#66CCFF',
		accentclr           => '#66CCFF',
		valuesclr           => '#660000',
		dclrs               => [qw(lred lgreen white #ffff77 black yellow)],
		bar_spacing         => 4,
		transparent         => 0,
		l_margin            => 5,
		b_margin            => 5,
		r_margin            => 5,
		t_margin            => 5,
		show_values         => 1
#		values_format       => "%4d",
);
###
%CONF=(); %PAR=();%ACCOUNT=();
###
local @month=qw(January February March April May June July August September October November December);
&par_prepare;

	my $m1=$month[$PAR{month1}-1];
	my $m2=$month[$PAR{month2}-1];
	local $period;
	if ($m1 eq $m2 && $PAR{day1} == $PAR{day2} && $PAR{year1}==$PAR{year2}){
		$period = "for $PAR{day1} $m1 $PAR{year1}";
	}else{
		$period = "from $PAR{day1} $m1 $PAR{year1} till $PAR{day2} $m2 $PAR{year2}";
	}


local $db=&db_prepare;
&proccess_images;
sub ord_to{
	my $what=shift;
	my $to=shift;
	$to=1 unless $to;
	my $tmp=int($what/$to);
	return ($tmp+1)*$to if ($tmp>0);
	return ($tmp-1)*$to ;
}
sub proccess_images{
	if($PAR{modelog} eq '' or $PAR{modelog} eq 'subscribers'){
		my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) =localtime($MY_TIME);
		$year+=1900;$mon++;
		$PAR{year1}=$year unless $PAR{year1};
		$PAR{year2}=$year unless $PAR{year2};
		$PAR{month1}=$mon unless $PAR{month1};
		$PAR{month2}=$mon unless $PAR{month2};
		$PAR{day1}=$mday unless $PAR{day1};
		$PAR{day2}=$mday unless $PAR{day2};
		&print_sent_messages unless $PAR{modelog};
		&print_subscribers if ($PAR{modelog} eq 'subscribers');
	}elsif($PAR{modelog} eq 'account'){
		&print_account;
	}else{
		printEmpty();
	}
}
sub print_sent_messages{
	my $data = GD::Graph::Data->new([]) or die GD::Graph::Data->error;
	my @WHERE=();
	push @WHERE, "`date` >=".$db->quote("$PAR{year1}-$PAR{month1}-$PAR{day1}");
	push @WHERE, "`date` <=".$db->quote("$PAR{year2}-$PAR{month2}-$PAR{day2}");	
	my $WHERE=join(" AND ",@WHERE);
	$WHERE="WHERE ".$WHERE if $WHERE;
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
$WHERE
GROUP BY pk_account
HAVING total_sent<>0 ORDER by name
ALL__
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	unless ($out->rows()){
		printEmpty;
	}else{
		while (my $output=$out->fetchrow_hashref){
			$data->add_point($output->{name},
				$output->{sent_manual},
				$output->{sent_sheduled},
				$output->{sent_sequential},
				$output->{sent_subscribe},
				$output->{sent_unsubscribe},
				$output->{sent_doubleoptin},				
			);	
		}
		my $width=($out->rows())*65;
		$width=600 if ($width<600);
		$my_graph = GD::Graph::bars->new($width,400) || die "Somthing wrong $!";
		$my_graph->set(@DEF_BLOKS) or warn $my_graph->error;
		my @t=$data->get_min_max_y_all();
		$my_graph->set( 
			x_label             => 'Accounts',
			y1_label            => 'Sent messages',
			cumulate           => 0,
			title               => "Sent messages ( $period )",
			#y1_max_value        => ord_to($t[1],int(int($t[1]/10)/100)*100),
			) or warn $my_graph->error;
		$my_graph->set_legend(qw|manual sheduled sequential subscribe unsubscribe doubleoptin|);
		print_graph($my_graph,$data);		
	}

}

sub print_subscribers{
	my $data = GD::Graph::Data->new([]) or die GD::Graph::Data->error;
	my @WHERE=();
	push @WHERE, "`date` >=".$db->quote("$PAR{year1}-$PAR{month1}-$PAR{day1}");
	push @WHERE, "`date` <=".$db->quote("$PAR{year2}-$PAR{month2}-$PAR{day2}");	
	my $WHERE=join(" AND ",@WHERE);
	$WHERE="WHERE ".$WHERE if $WHERE;
	my $sql=<<ALL__;
SELECT  `name`,`pk_account` ,    
SUM(`subscribers`) as subscribers ,  
SUM(`unsubscribers`) as unsubscribers,
SUM(`subscribers`)-SUM(`unsubscribers`) as  total_subscribers
FROM  `${PREF}stat_account_dayly` 
RIGHT JOIN ${PREF}account ON pk_account=fk_account
$WHERE
GROUP BY pk_account
HAVING subscribers<>0 OR unsubscribers<>0 
ORDER by name
ALL__
	my $out=$db->prepare($sql);
	$out->execute();
	&Error($sql);
	unless ($out->rows()){
		printEmpty;
	}else{
		while (my $output=$out->fetchrow_hashref){
			$data->add_point($output->{name},
				-$output->{unsubscribers},
				$output->{subscribers},
				
			);	
		}
		my $width=($out->rows())*45;
		$width=600 if ($width<600);
		$my_graph = GD::Graph::bars->new($width,400) || die "Somthing wrong $!";
		$my_graph->set(@DEF_BLOKS) or warn $my_graph->error;
		my @t=$data->get_min_max_y_all();
		$my_graph->set( 
			x_label             => 'Accounts',
			y1_label            => 'Count of prospects'." $t[0] $t[1]",
			cumulate           => 0,
			title               => "Subscribers/unsubscribers ( $period )",
			zero_axis	=>1,
			text_space=>4,
			overwrite=>1
			#y1_max_value        => 300 ,
			#y1_min_value        => -300 ,
			) or warn $my_graph->error;
		$my_graph->set_legend(qw| unsubscribers subscribers |);
		print_graph($my_graph,$data);		

	}

}
sub print_account{
	my $data = GD::Graph::Data->new([]) or die GD::Graph::Data->error;
	my $sql="select * from ${PREF}account";
	my $out=$db->prepare($sql);
	$out->execute();
	my %accountname;
	while (my %output=%{$out->fetchrow_hashref}){
		$accountname{$output{pk_account}}=$output{name};
	}
	unless(%accountname){
		printEmpty();
	}
	foreach my $account_id(sort {$accountname{$a} cmp $accountname{$b}}keys %accountname){
		$data->add_point($accountname{$account_id},
			GetSQLCount("Select * from ${PREF}user WHERE fk_account=? AND  isact<>1",$account_id),
			GetSQLCount("Select * from ${PREF}user WHERE fk_account=? AND  isact=1",$account_id));
	}
	#my @tmpmax=();
	#foreach(0..scalar(keys %accountname)-1){
	#	push(@tmpmax,$data->get_y_cumulative($_,1));
	#}
	#@tmpmax=sort{$b<=>$a}@tmpmax;
	#$max=$tmpmax[0];
	my $width=(scalar(keys %accountname)+1)*45;
	$width=600 if ($width<600);
	$my_graph = GD::Graph::bars->new($width,400) || die "Somthing wrong $!";
	$my_graph->set(@DEF_BLOKS) or warn $my_graph->error;
	my @t=$data->get_min_max_y_all();
	$my_graph->set( 
		x_label             => 'Accounts',
		y1_label            => 'Active/inactive prospects',
		cumulate           => 1,
		title               => "Count of prospects",
		#y1_max_value        => ord_to($t[1],int($t[1]/10)),
	) or warn $my_graph->error;
	$my_graph->set_legend("inactive prospects",'active prospects');
	print_graph($my_graph,$data);
}
#http://muiresp/cgi-bin/logpng.cgi?rec_key=&ses=ozorA27ZEzd03pv6H8JbNQWa0&act=&act2=log&referer=&modelog=total_prospects&issubmit=1&fk_admin=1&submit2=Show&day1=26&day2=26&month1=4&month2=4&year1=2003&year2=2003
##################################


sub print_graph{ 
	my $my_graph=shift;
	my $data=shift;
	my $format = $my_graph->export_format;
	print "Pragma: no-cache\n";
	print $q->header("image/$format");
	binmode STDOUT;
	print $my_graph->plot($data)->$format();
}
