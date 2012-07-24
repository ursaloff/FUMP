#!/usr/bin/perl
#################################################################
#FILE: hfparser.pm
#HTML FORM PARSING MODULE
#################################################################
package repparser;
use hfparser;
#use Carp;
use POSIX;
use CGI;
push (@ISA,"hfparser");
#use strict;
use vars qw($VERSION $DEF_ON_PAGE $DEF_PAGE_PAGES $q %FL $PAGE_PAR_NAME $PAGE_PAGES_PAR_NAME %FLAGS);
#@EXPORT=qw($q);
$VERSION='1.4';
###############
#defaults
$DEF_ON_PAGE=30;
$DEF_PAGE_PAGES=20;
$PAGE_PAR_NAME="page";
$PAGE_PAGES_PAR_NAME="page2";
#############################################
sub new {
	my $classname=shift;
	my $self = {};
	bless ($self,$classname);
	$q=$hfparser::q;
	$self->_init(@_);
	return $self;
}
#############################################
sub _init{
	my $self=shift;
	$self->SUPER::_init(@_);
	##New class implementation put here
	$self->{page_now}=$q->param($PAGE_PAR_NAME);
	$self->{page_now}=1 unless $self->{page_now};
	$self->{page_pages}=$DEF_PAGE_PAGES unless $self->{page_pages};
	$self->{onpage}=$DEF_ON_PAGE unless $self->{onpage};
	$self->{onpage}=$q->param('rponpage') if $q->param('rponpage');
	foreach my $val(qw(30 50 100 200 400 500 1000)){
		$self->add_element('rponpage',$val);
	}
	$self->set_def('rponpage',$self->{onpage});
	######Page line defaults
	$self->{PAGE_LINE_SHABL}{linkattr}={class=>"menu"} unless defined $self->{PAGE_LINE_SHABL}{linkattr};
	$self->{PAGE_LINE_SHABL}{linebefore}="Total: <B>{rec_count}</B>  in <B>{rec_pages}</B> pages:" unless defined $self->{PAGE_LINE_SHABL}{linebefore};
	$self->{PAGE_LINE_SHABL}{lineafter}="" unless defined $self->{PAGE_LINE_SHABL}{lineafter};
	$self->{PAGE_LINE_SHABL}{act_element}=" <B>[#]</B> ";
	$self->{PAGE_LINE_SHABL}{link_element}=" [#] ";
	$self->{PAGE_LINE_SHABL}{nextpages}=" Next&gt;&gt;&gt; " unless $self->{PAGE_LINE_SHABL}{nextpages};
	$self->{PAGE_LINE_SHABL}{prevpages}=" &lt&lt;&lt;Prev " unless $self->{PAGE_LINE_SHABL}{prevpages};
}
#############################################
sub SetPagelineProp{
	my $self=shift;
	my %param=@_;
	if ($param{onpage}){
		$self->{onpage}=$param{onpage};	delete($param{onpage});
	}
	if ($param{page_pages}){
		$self->{page_pages}=$param{page_pages};delete($param{page_pages});
	}
	foreach my $key(keys %param){
		$self->{PAGE_LINE_SHABL}{$key}=$param{$key};
	}
}
#############################################
sub GetAllCount{
	my $self=shift;
	if ( defined($self->{ALL_ROWS_COUNT})){
		return $self->{ALL_ROWS_COUNT}
	}else{
		return scalar @{$self->GetRepDataArray};
	}
}
sub GetRepDataArray{
	my $self=shift;
	unless (ref($self->{REP_DATA_ARRAY}) eq 'ARRAY'){
		$self->{REP_DATA_ARRAY}=[];
	}
	return	$self->{REP_DATA_ARRAY};
}
sub GetPagesCount{
	my $self=shift;
	return ceil($self->GetAllCount/$self->{onpage});
}
##############
sub AddRow{
	my $self=shift;
	my $row_ref=shift;
	if (defined  $row_ref){
		push(@{$self->GetRepDataArray},$row_ref);
	}
}
sub GetLimitString{
	my $self=shift;
	my $starting_from=($self->{page_now}-1)*$self->{onpage};
	return "LIMIT $starting_from , $self->{onpage}";
}
####################
sub GetReportRows{
	my $self=shift;
	my $out;
	my $count;
	my $mode_sent_only_required_data;
	my $start;
	my $end;
	if ($self->GetAllCount != scalar(@{$self->GetRepDataArray})){
		$mode_sent_only_required_data=1;
		$start=1;
		$end=scalar(@{$self->GetRepDataArray});
	}else{
		#need filter
		$mode_sent_only_required_data=0;
		$start=($self->{page_now}-1)*$self->{onpage}+1;
		$end=$self->{page_now}*$self->{onpage};
	}
	$end=@{$self->GetRepDataArray} if $end>scalar(@{$self->GetRepDataArray});
	my $count_templates=scalar(@{$self->{REP}{ROW}});
	my $template_now=0;
	foreach my $rowref(@{$self->GetRepDataArray}[$start-1..$end-1]){
		$count++;$template_now++;
		$template_now=1 if ($template_now > $count_templates);
		my @rows=@{$self->{REP}{ROW}};
		my $row=$rows[$template_now-1];
		my %row=%{$rowref};
		$row{'#'}=$self->{onpage}*($self->{page_now}-1)+$count;
		$row{'##'}=$count;
		foreach my $keyrow(keys %row){
			$row=~s/\{r_$keyrow\}/$row{$keyrow}/gs;	
		}
		$out.=$row;
	}

	$self->add_regesp('{RP_SHOWRECORDS}',$count);
	return $out;
}
###################
sub ParseReport{
	my $self=shift;
	local %FL;
	$FL{REPORT}="_";
	$FL{HEADER}="_header_";
	$FL{ROW}="_row_";
	$FL{FOOTER}="_footer_";
	$FL{EMPTY}="_empty_";
	local %FLAGS;
	foreach(keys %FL){
		$FLAGS{$_}{start}="<!--rep$FL{$_}start-->";
		$FLAGS{$_}{end}="<!--rep$FL{$_}end-->";
	}
	my $alldata=$self->as_string;
	$alldata=~s/$FLAGS{REPORT}{start}(.*?)$FLAGS{REPORT}{end}/{ALL_REPORT}/gs;
	$self->{REP}{ALL}=$1;
	$self->{REP}{HEADER}=INSIDE($self->{REP}{ALL},$FLAGS{HEADER}{start},$FLAGS{HEADER}{end});
	$self->{REP}{FOOTER}=INSIDE($self->{REP}{ALL},$FLAGS{FOOTER}{start},$FLAGS{FOOTER}{end});	
	my $row=INSIDE($self->{REP}{ALL},$FLAGS{ROW}{start},$FLAGS{ROW}{end});
	my @rows=split(/<!--ROW_DELMITTER-->/,$row);
	$self->{REP}{ROW} = \@rows;
	$self->{REP}{EMPTY} =INSIDE($self->{REP}{ALL},$FLAGS{EMPTY}{start},$FLAGS{EMPTY}{end});	
	unless ($self->GetAllCount){
		$alldata=~s/{ALL_REPORT}/$self->{REP}{EMPTY}/gs; 
	}else{
		$alldata=~s/{ALL_REPORT}/$self->{REP}{HEADER} {report_rows} $self->{REP}{FOOTER}/gs;
		$self->add_regesp('{report_rows}',GetReportRows($self));
	}
	$self->{ALL_DATA}=$alldata;
}
sub GetURLToExport{
	my $self=shift;
	return get_full_url({export_to_txt=>1})
}
###############################
sub INSIDE{
	my $str=shift;
	my $val1=shift;
	my $val2=shift;
	if($str=~/$val1(.*?)$val2/gis){
		return $1;
	}else{
		return "$val1 Not found $val2";
	}
}
sub get_full_url{
	my $pars=shift;
	my %pars=%{$pars};
	#my $q = new CGI;
	my %tmp;
	foreach (keys %pars){
		$tmp{$_}=$q->param($_) if $q->param($_);
		$q->delete($_);
		$q->param($_,$pars{$_})
	}
	my $url=$q->url(-absolute=>1,-query=>1);
	map{$q->param($_,$tmp{$_})}keys %tmp;
	return $url;
}

##############################
sub GetPageLine{
	my $self=shift;
	my $out;
	return "" unless $self->{onpage};
	return "" if $self->{onpage}>$self->GetAllCount;
	my($startpage,$endpage);
	my($startlink,$endlink);
	if ($self->GetPagesCount>1){
		my $pagepeges=ceil($self->{page_now}/$self->{page_pages});
		$startpage=($pagepeges-1)*$self->{page_pages}+1;
		$endpage=$startpage+$self->{page_pages}-1;
		$endpage=$self->GetPagesCount if ($endpage>$self->GetPagesCount);
		my $attr=$self->{PAGE_LINE_SHABL}{linkattr};
		if ($startpage>1){
			$attr->{href}=get_full_url({page=>$startpage-1});
			$startlink=$q->a($attr,$self->{PAGE_LINE_SHABL}{prevpages});		
		}
		if ($endpage<$self->GetPagesCount){
			$attr->{href}=get_full_url({page=>$endpage+1});
			$endlink=$q->a($attr,$self->{PAGE_LINE_SHABL}{nextpages});		
		}
		foreach my $p($startpage..$endpage){
			unless ($p eq $self->{page_now}){
				my $discr=$self->{PAGE_LINE_SHABL}{link_element};
				$discr=~s/#/$p/;
				$attr->{href}=get_full_url({page=>$p});
				$out.=$q->a($attr,$discr);
			}else{
				my $discr=$self->{PAGE_LINE_SHABL}{act_element};
				$discr=~s/#/$p/;
				$out.=$discr;
			}
		}
	}
	foreach ($self->{PAGE_LINE_SHABL}{linebefore},$self->{PAGE_LINE_SHABL}{lineafter}){
		s/{rec_pages}/$self->GetPagesCount/ge;
		s/{rec_count}/$self->GetAllCount/ge;
	}
	return "$self->{PAGE_LINE_SHABL}{linebefore} $startlink $out $endlink $self->{PAGE_LINE_SHABL}{lineafter}" ;
}
###########################
sub ParseData{
	my $self=shift;
	$self->add_regesp('{RP_ALLRECORDS}',$self->GetAllCount);
	$self->add_regesp('{RP_PAGE_LINE}',$self->GetPageLine);
	$self->ParseReport;
#$self->add_regesp('{report_rows}',);
	$self->SUPER::ParseData;
}
######
1;
