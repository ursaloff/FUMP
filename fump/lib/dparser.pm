#!/usr/bin/perl
#################################################################
#FILE: dparser.pm
#TEXT DATA PARSING MODULE
#################################################################
package dparser;
use strict;
use vars qw(@ISA);
$dparser::VERSION='1.5';
$dparser::is_cript_default=0;
$dparser::is_translate=1;
$dparser::files_cash={};
$dparser::lang={};
sub new {
	my $classname=shift;
	my $self = {};
	bless ($self,$classname);
	$self->_init(@_);
	return $self;
}
#############################################
sub _init{
	my $self=shift;
	###DEFAULT###
	$self->_set_defaults;
	###INIT_DATA - OVERVRITE DEFAULTS
	if (@_){
		my %extra= @_;
		foreach (keys %extra){
			$self->{$_}=$extra{$_};
		}
	}
	#####LOAD DATA FROM SOURCE
	$self->_load_data;
	###ADDITIONAL PARSING
}
######
sub _set_defaults{
	my $self=shift;
	$self->{SOURCE}='file';
	$self->{STRING_DELMITTER}="\n";
	$self->{IS_CRIPT}=$dparser::is_cript_default;
}
######
sub _load_data{
	my $self=shift;
	#local $\="";
	if ($self->{'SOURCE'}=~/^file/i){
		if($dparser::files_cash->{$self->{DATA}}){
			$self->{ALL_DATA}=$dparser::files_cash->{$self->{DATA}};
		}else{
			my $filename=$self->{DATA};
			$self->{DATA}=~s/\.html$/.dat/ if $self->{IS_CRIPT};
			open(FILE,$self->{DATA}) || die "dparser :: Can not load data from FILE $self->{DATA} - $!";
			while(<FILE>){$self->{ALL_DATA} .= $_;}
			close(FILE);			
			$self->{ALL_DATA}=loaddata($self->{ALL_DATA}) if $self->{IS_CRIPT};
			$dparser::files_cash->{$filename}=$self->{ALL_DATA};
		}
	}elsif($self->{'SOURCE'}=~/^handle/i){
		my $handle=$self->{DATA};
		while(<$handle>){$self->{ALL_DATA} .= $_;}
	}elsif(($self->{'SOURCE'}=~/^string/i)){
		$self->{ALL_DATA}=$self->{DATA};
	}elsif(($self->{'SOURCE'}=~/^array_ref/i)){
		$self->{ALL_DATA}=join("\n",@{$self->{DATA}});
	}else{
		die "DataParser: Can not understand the SOURCE value it must be  file|handle|string|array_ref";
	}
	unless($self->{'SOURCE'}=~/^file/i){
		$self->{ALL_DATA}=loaddata($self->{ALL_DATA}) if $self->{IS_CRIPT};
	}
	if ($self->{FROM} and $self->{TO}){
		if($self->{ALL_DATA}=~/$self->{FROM}(.*?)$self->{TO}/s){
			$self->{ALL_DATA}=$1;
		}else{
			die "dparser :: Can not find separators $self->{FROM} and $self->{TO} anywhere in the file $self->{ALL_DATA}";
		}
	}
	#Translate
	if($dparser::is_translate){
		$self->{ALL_DATA}=~s/\[LNG_(.+?)\]/translate($1)/ge;
	}
	
}
##################
sub loaddata{
	my $what=shift;
	$what=~tr/abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/DNfeQS5Ouj6rMkIg9PwTXHzC1Vc3vEA8nxlLF7KYbsUmJhZ4WoRqiGpy0aBd2t/;
	$what =~ s/_([\dA-Fa-f][\dA-Fa-f])/pack ("C", hex ($1))/eg;
	return $what;
}
######  CutArray
sub SplitData{
	my $self=shift;
	my $befor=shift;
	my $after=shift;
	$after=$befor unless $after;
	$self->{BEFORE}=undef;
	$self->{INSIDE}=undef;
	$self->{AFTER}=undef;
	if ($self->{ALL_DATA}=~/^(.*?)$befor(.*?)$after(.*)$/s){
		$self->{BEFORE}=$1;
		$self->{INSIDE}=$2;
		#die "Inside: $self->{INSIDE}";
		$self->{AFTER}=$3;
		return 1;
	}else{
		die "dparser::SplitData can not find separators: $befor and $after main data is $self->{ALL_DATA}";
	}
	return 0;
}
sub getBEFORE{
	my $self=shift;
	return $self->{BEFORE} if $self->{BEFORE};
	my $first=shift;
	my $second=shift;
	$second=$first unless $second;
	if ($self->{ALL_DATA}=~/^(.*?)$first/s){
		return $1;
	}
	
}
sub getINSIDE{
	my $self=shift;
	return $self->{INSIDE} if $self->{INSIDE};
	my $first=shift;
	my $second=shift;
	$second=$first unless $second;
	if ($self->{ALL_DATA}=~/$first(.*?)$second/s){
		return $1;
	}
}
sub getAFTER{
	my $self=shift;
	return $self->{AFTER} if $self->{AFTER};
	my $first=shift;
	my $second=shift;
	$second=$first unless $second;
	if ($self->{ALL_DATA}=~/$second(.*)$/s){
		return $1;
	}
}

sub deleteBEFORE_AFTER{
	my $self=shift;
	$self->{ALL_DATA}=$self->getINSIDE(@_);
}
sub replaceINSIDE{
	my $self=shift;
	my $what=shift;
	$self->{ALL_DATA}=$self->getBEFORE(@_).$what.$self->getAFTER(@_);
}
sub deleteINSIDE{
	my $self=shift;
	$self->replaceINSIDE("",@_);
}
sub Hide{
	my $self=shift;
	my $first=shift;
	my $second=shift;
	$second=$first unless $second;
	$self->{ALL_DATA}=~s/$first.*?$second//gs;
}

sub add_regesp{
	my $self=shift;
	my $patten=shift;
	my $replace=shift;
	$self->{REGESP}{$patten}=$replace if $patten;
}
#######
sub add_func{
	my $self=shift;
	my $patten=shift;
	my $replace=shift;
	$self->{FUNC}{$patten}{f_ref}=$replace if $patten;
	$self->{FUNC}{$patten}{args}=[@_] if $patten;
}
#######
sub add_parsing{
	my $self=shift;
	my $func_ref=shift;
	push(@{$self->{PARSING}},$func_ref);
}
#####################################
sub ChangeData{
###CHANGING TEMPLATE BEFOR PARSING
	my $self=shift;
	my $patten = shift;
	my $replace= shift;
	return unless $patten;
	#my $str=join("<BR>",map{"{fm_text_name$_}"}(1..50));
	$self->{ALL_DATA}=~s/$patten/$replace/;
}
sub translate{
	my $key=shift;
	my $lng=$dparser::lang;
	return("<FONT color=red><b>Can not find key $key</b></font>") unless exists $lng->{$key};
	return  "$lng->{$key}";
}
########
sub ParseData{
	my $self=shift;
	#foreach my $name(keys %{$dparser::GlobalRegesps}){
	#	$self->add_regesp($name,$dparser::GlobalRegesps->{$name});
	#}
###############
	my (%regesp,%functions,@parsing);
	%regesp=%{$self->{REGESP}} if (exists($self->{REGESP}));
	%functions=%{$self->{FUNC}} if (exists($self->{FUNC}));
	@parsing=@{$self->{PARSING}} if (exists($self->{PARSING}));
	foreach my $reg (keys %regesp){
		$regesp{$reg}=~s/$reg//gs;
		$self->{ALL_DATA}=~s/$reg/$regesp{$reg}/g;
	}
	foreach my $reg (keys %{$dparser::GlobalRegesps}){
		my $to=$dparser::GlobalRegesps->{$reg};
		$self->{ALL_DATA}=~s/$reg/$to/g;
	}	
	foreach my $funk_id (keys %functions){
		next unless ref($functions{$funk_id}{f_ref});
		my @args=@{$functions{$funk_id}{args}};
		my $fref=$functions{$funk_id}{f_ref};
		$self->{ALL_DATA}=~s/$funk_id/&{$fref}(@args)/gse;
	}
	foreach my $parse (@parsing){
		local $_=$self->{ALL_DATA};
		&$parse($self);
		$self->{ALL_DATA}=$_;
	}
###############
#For FUMP 
	$self->Hide('<!--hide-->','<!--endhide-->');
	$self->{ALL_DATA}=~s/src\s*=\s*"?img\/([a-z0-9_]+?)\.(png|jpg|gif)"?/src="content.cgi?get=image&mode=$2&f=$1"/gis;
	$self->{ALL_DATA}=~s/style\.css/content.cgi?get=css"/gs;
#########		
}
######
sub get {
	my $self = shift;
	my $what=shift;
	return $self->{$what};
}
##################
sub as_string {
	my $self = shift;
	return $self->{ALL_DATA};
}
###########################
sub print{
	my $self = shift;
	print $self->as_string;
}
######
sub as_array{
	my $self=shift;
	my @strings=split(/\n/,$self->as_string);
	chomp(@strings);
	return @strings;
}
1;
###########################



