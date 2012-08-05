package Mail::DeliveryStatus::BounceValidator;
=head1 NAME

Mail::DeliveryStatus::BounceValidator - Perl extension to analyze bounce messages

=head1 SYNOPSIS

  use Mail::DeliveryStatus::BounceValidator;

  my $bounce = eval { Mail::DeliveryStatus::BounceValidator->new( \*STDIN | $fh | "entire\nmessage" | ["array","of","lines"] ) };
  if ($@) { } # couldn't parse.

 
=head1 ABSTRACT

Mail::DeliveryStatus::BounceValidator analyzes  bounce
messages and returns a structured description of the
addresses that bounced and the reason they bounced; it also
returns information about the original returned message
including the Message-ID.  It works best with RFC1892
delivery reports, but will gamely attempt to understand any
bounce message no matter what MTA generated it.

=head1 DESCRIPTION

I wrote this for the Listbox v2 project; good mailing list
managers handle bounce messages so listowners don't have
to.  The best mailing list managers figure out exactly
what is going on with each subscriber so the appropriate
action can be taken.

=cut --------------------------------------------------

use 5.00503;
#use lib('../..');
use strict;
use vars qw($VERSION $DEBUG $verbose);
$VERSION = '1.1';
$DEBUG = 0;
$verbose=0;
use MIME::Parser;
#use Mail::Verp;
sub log {
  my $self = shift;
  if (ref $self->{'log'} eq "CODE") { 
	  $self->{'log'}->(@_);
	  }
  return 1;
}

sub new {
  # my $bounce = Mail::DeliveryStatus::BounceValidator->new( \*STDIN | $fh | "entire\nmessage" | ["array","of","lines"] );

  # XXX: It turns out that MIME::Decoder::QuotedPrint (in MIME-tools up to
  # at least 5.417) assigns to $_ without localizing it first (see
  # http://rt.cpan.org/NoAuth/Bug.html?id=11802).  There are various code
  # paths that can lead to QP messages being decoded or encoded, so to
  # simplify matters, we do this before anything else.
  local $_;

  my $class = shift;
  my $parser = new MIME::Parser;
  ##OPTIMAIZE PARSER
  $parser->output_to_core(1);
  #$parser->tmp_to_core(1);
  my $message;

  my %opts   = (); for (reverse 0 .. $#_) { if (ref $_[$_] eq "HASH" ) { %opts  = (%opts, %{$_[$_]}); splice(@_, $_, 1) } }

=head2 new()

OPTIONS.  If you pass BounceParser->new(..., {log=>sub { ... }}) That will be used as a logging callback.
	
	my $validator=new Mail::DeliveryStatus::BounceValidator(\*F,{'log'=>sub{print shift()."\n"}});

=cut

  if    (not @_)               { print STDERR "BounceParser: expecting bounce mesage on STDIN\n" if -t STDIN;
				 $message = $parser->parse(\*STDIN); }
  elsif (not ref $_[0])        { $message = $parser->parse_data(@_); }
  elsif (ref $_[0] eq "ARRAY") { $message = $parser->parse_data(@_); }
  else                         { $message = $parser->parse(@_);      }

  my $self = bless { diagnostics   => {},
		     is_bounce => 0,
		     'log'     => $opts{'log'} || sub { },
		     parser    => $parser,
		     message   => $message
		   }, $class;
 $self->parse_bounce();	
 return $self;
}
=pod

=item is_bounce

	my $bounce = eval { Mail::DeliveryStatus::BounceValidator->new( \*STDIN | $fh | "entire\nmessage" | ["array","of","lines"] ) };
	my $is_bounced= $bounce->is_bounce($entity);
	
Returns true value if message is bounced

=cut
sub is_bounce{
	my $self=shift;
	if (exists($self->{is_bounce})){
		return $self->{is_bounce};
	}else{
			return 0;
	}
}
sub email{
	return shift->{email};
}
sub diagnostics{
	return shift->{diagnostics};
}
sub message{
	return shift->{message};
}
sub hardsoft{
	return shift->diagnostics()->{_hardsoft};
}

#=pod
#
#=item find_verp
#
#	my $email= find_verp($entity);
#	
#Please look at Mail::Verp manual for details
#
#=cut
#
#sub find_verp { 
#
#	my $entity = shift; 
#	my $mv = Mail::Verp->new;
#		
#	my ($sender, $recipient) = $mv->decode($entity->head->get('To', 0));
#	return $recipient || undef; 
#
#
#}
=pod

=item strip

	my $str = strip($str);  
   
a simple subroutine to take off leading and trailing white spaces

=cut

sub strip { 
my $string = shift || undef; 
	if($string){ 
		$string =~ s/^\s+//o;
		$string =~ s/\s+$//o;
		return $string;
	}else{ 
		return undef; 
	}
}
sub trim { 
	my $string = shift || undef; 
	return strip($string);
}

sub generic_delivery_status_parse { 
	my $entity = shift; 
	my $diag = {}; 
	my $email; 
		# sanity check
		#if($delivery_status_entity->head->mime_type eq 'message/delivery-status'){ 	
			my $body = $entity->bodyhandle;
			my @lines;
			my $IO; 
			my %bodyfields;
			if($IO = $body->open("r")){ # "r" for reading.  
				while (defined($_ = $IO->getline)){ 
					if ($_ =~ m/(.+?)\:(.+)/){ 
						my ($k, $v) = ($1,$2);
						chomp($v); 
						#$bodyfields{$k} = $v;
						$diag->{$k} = $v; 
					}
				} 
				$IO->close;
			}
			
			if($diag->{'Diagnostic-Code'} =~ /X\-Postfix/){
				$diag->{Guessed_MTA} = 'Postfix';
			} 
			
			my ($rfc, $remail) = split(';', $diag->{'Final-Recipient'});
			if($remail eq '<>'){ #example: Final-Recipient: LOCAL;<>
			 	($rfc, $remail) = split(';', $diag->{'Original-Recipient'});
			}
			$email = $remail; 
		foreach(keys %$diag){ 
			$diag->{$_} = strip($diag->{$_}); 
		}
	return ($email, $diag); 
}


sub find_delivery_status {

	my $entity = shift; 
	my @parts = $entity->parts; 
	my $email; 

	my $diag = {}; 
		
	if(!@parts){ 
		if($entity->head->mime_type eq 'message/delivery-status'){ 
			($email, $diag) = generic_delivery_status_parse($entity); 
	    	return ($email, $diag); 
		} 
	}else{ 
		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			($email, $diag) = find_delivery_status($part); 
			if(($email) && (keys %$diag)){ 
				return ($email, $diag); 
			}
		}
	}
}
sub generic_parse { 
	my $self=shift;
	my $entity = shift; 
	my ($email, $list); 
	my $diag = {}; 
	($email, $diag) = find_delivery_status($entity); 	
	$list=1;
	#$list = find_list_in_list_headers($entity); 
	#$list ||= generic_body_parse_for_list($entity); 
	$email = strip($email);
	$email =~ s/^\<|\>$//g if $email;  
	$list  = strip($list) if $list; 
	return ($list, $email, $diag); 
	
}
sub diagnostic_as_string{
	my $self=shift;
	my $diag=$self->diagnostics;
	my $str;
	if(ref $diag eq "HASH"){
		map{$str.=$_.": ".$diag->{$_}."\n"}keys %$diag; 
	}else{
		return "Not a HASH";
	}
	return "$str";
}

sub set_bounced_flag{
	my $self=shift;
	return if($self->is_bounce);
	my ($email,$diagnostics,$when)=@_;
	$diagnostics->{FoundBy}=$when;
	if($email){
		$self->{is_bounce}=1;
		$self->{email}=$email;
		$self->{diagnostics}=$diagnostics;
	}
#	if($email and scalar(keys %{$diagnostics})){
#		$self->log("email: $email");
#		$self->log("diagnostics\n".$self->diagnostic_as_string($diagnostics));		
#	}
}

sub parse_for_qmail {

	# When I'm bored
	# => http://cr.yp.to/proto/qsbmf.txt
	# => http://mikoto.sapporo.iij.ad.jp/cgi-bin/cvsweb.cgi/fmlsrc/fml/lib/Mail/Bounce/Qmail.pm
	my $self= shift;	
	my $entity = shift;	
	my ($email, $list); 
	my $diag = {}; 
	my @parts = $entity->parts; 
	
	my $state        = 0;
	my $pattern      = 'Hi. This is the';
	my $pattern2     = 'Your message has been enqueued by';
	
	my $end_pattern  = '--- Undelivered message follows ---';
	my $end_pattern2 = '--- Below this line is a copy of the message.';
	my $end_pattern3 = '--- Enclosed is a copy of the message.';
	my $end_pattern4 = 'Your original message headers are included below.';
	
	my ($addr, $reason);
		
	if(!@parts){ 
		my $body = $entity->bodyhandle; 
		my $IO;
		if($body){ 
			if($IO = $body->open("r")){ # "r" for reading.  
				while (defined($_ = $IO->getline)){ 
					
					my $data = $_;
					$state = 1 if $data =~ /$pattern|$pattern2/;
					$state = 0 if $data =~ /$end_pattern|$end_pattern2|$end_pattern3/;
					
					if ($state == 1) {	
						$data =~ s/\n/ /g;
	
						if($data =~ /\t(\S+\@\S+)/){ 
							$email = $1; 
						} elsif ($data =~ /\<(\S+\@\S+)\>:\s*(.*)/) {
							($addr, $reason) = ($1, $2);	
							 $diag->{Action} = $reason;
							my $status = '5.x.y';
							if($data =~ /\#(\d+\.\d+\.\d+)/) {
								$status = $1;
							}elsif ($data =~ /\s+(\d{3})\s+/) {
								my $code = $1;
								$status  = '5.x.y' if $code =~ /^5/;
								$status  = '4.x.y' if $code =~ /^4/;
							
							    $diag->{Status} = $status;
								$diag->{Action} = $code; 
								
							}
						
							$email                 = $addr; 
							$diag->{Guessed_MTA}   = 'Qmail'; 
							
						}elsif ($data =~ /(.*)\s\(\#(\d+\.\d+\.\d+)\)/){		# Recipient's mailbox is full, message returned to sender. (#5.2.2)

								$diag->{'Diagnostic-Code'} = $1; 
								$diag->{Status}            = $2; 
								$diag->{Guessed_MTA}       = 'Qmail'; 
								
						}elsif($data =~ /Remote host said:\s(\d{3})\s(\d+\.\d+\.\d+)\s\<(\S+\@\S+)\>(.*)/){ 	# Remote host said: 550 5.1.1 <xxx@xxx>... Account is over quota. Please try again later..[EOF] 

						$diag->{Status}             = $2; 
						$email                      = $3; 
						$diag->{'Diagnostic-Code'}  = $4;
						$diag->{Action}             = 'failed'; #munging this for now...
						$diag->{'Final-Recipient'}  = 'rfc822'; #munging, again. 
						
						}elsif($data =~ /Remote host said:\s(.*?)\s(\S+\@\S+)\s(.*)/){ 
							
							my $status;	
							$email                   ||= $2; 


							$status                  ||= $1;
							$diag->{Status}          ||= '5.x.y' if $status =~ /^5/;
							$diag->{Status}          ||= '4.x.y' if $status =~ /^4/;
							$diag->{'Diagnostic-Code'} = $data;
							$diag->{Guessed_MTA}       = 'Qmail'; 
						
						}elsif ($data =~ /Remote host said:\s(\d{3}.*)/){ 
						
							$diag->{'Diagnostic-Code'} = $1; 
						
						}elsif ($data =~ /(.*)\s\(\#(\d+\.\d+\.\d+)\)/){ 
						
							$diag->{'Diagnostic-Code'} = $1; 
							$diag->{Status}            = $2;
						
						}elsif ($data =~ /(No User By That Name)/){ 
						
							$diag->{'Diagnostic-Code'} = $data; 
							$diag->{Status} = '5.x.y';
						
						}elsif ($data =~ /(This address no longer accepts mail)/){ 
						
							$diag->{'Diagnostic-Code'} = $data; 
						
						}elsif($data =~ /The mail system will continue delivery attempts/){ 
							$diag->{Guessed_MTA}       = 'Qmail'; 
							$diag->{'Diagnostic-Code'} = $data;
						}
					}
				}
			}
			
			$list =1;
			return ($list, $email, $diag); 
		}else{ 
			# no body part to parse
			return (undef, undef, {});
		}
	}else{ 
		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			($list, $email, $diag) = $self->parse_for_qmail($part); 
			if(($email) && (keys %$diag)){ 
				return ($list, $email, $diag); 
			}
		}
	}
}

sub parse_for_exim { 
	my $self = shift;	
	my $entity = shift;	
	my ($email, $list); 
	my $diag = {}; 
	
	my @parts = $entity->parts;
	if(!@parts){ 
		if($entity->head->mime_type =~ /text/){ 
			# Yeah real hard. Bring it onnnn!
			if($entity->head->get('X-Failed-Recipients', 0)){ 
				
				$email                  = $entity->head->get('X-Failed-Recipients', 0);
				$email                  =~ s/\n//; 
				$email                  = trim($email); 
				$list                   = 1;
				$diag->{Status}         = '5.x.y'; 
				$diag->{Guessed_MTA}    = 'Exim'; 
				# unrouteable mail domain
				my $body = $entity->bodyhandle;
				my $IO;
				my $text;
				if($body){ 
					if($IO = $body->open("r")){ # "r" for reading.  
						while(defined($_ = $IO->getline)){
							$text.=$_;
							my $data = $_;
							if(/(unrouteable mail domain ".*?")/i){
								$diag->{'Diagnostic-Code'} = ucfirst(strip($1));
								$diag->{'Action'} = 'failed';
								$diag->{'Status'} = '5.4.4';
								last;
							}
						}						
					}
				}
				unless($diag->{'Status'} eq '5.4.4'){
					my $end_pattern = '------ This is a copy of the message';
					if($text=~/$end_pattern/){
						my ($mess,$copy)=split(/$end_pattern/,$text);
						my @mess_lines=split(/\n/,$mess);
						chomp(@mess_lines);
						my $is_diag=0;
						my @diag=();
						foreach my $line(@mess_lines){
							$line=strip($line);
							if ($line=~/^(\S+\@\S+)$/){
								$is_diag=1;
								next;
							}
							if($is_diag){
								push(@diag,$line);
							}
						}
						if(@diag){
							$diag->{'Diagnostic-Code'} = ucfirst(join(" ",@diag));
							if($diag->{'Diagnostic-Code'}=~/([54]\.[0-9]\.[0-9])/g){
								$diag->{'Status'} = $1;								
							}
						}
					}
				}
				return ($list, $email, $diag);
				
			}else{ 
				
				my $body = $entity->bodyhandle; 
				my $IO;
				if($body){ 
				
					if($IO = $body->open("r")){ # "r" for reading.  
						
						my $pattern     = 'This message was created automatically by mail delivery software (Exim).';
						my $end_pattern = '------ This is a copy of the message';
						my $state       = 0;
						
						while (defined($_ = $IO->getline)){ 
						
							my $data = $_;
						
							$state = 1 if $data =~ /\Q$pattern/;
							$state = 0 if $data =~ /$end_pattern/;
						
							if ($state == 1) {
						
								$diag->{Guessed_MTA} = 'Exim';
					
								if($data =~ /(\S+\@\S+)/){
						
									$email = $1;
									$email = trim($email);
						
								}elsif($data =~ m/unknown local-part/){ 
						
									$diag->{'Diagnostic-Code'} = 'unknown local-part';
									$diag->{'Status'}          = '5.x.y';
						
								}	
							}
						}
					}
				}
				return ($list, $email, $diag);
			} 
		}else{ 
			return (undef, undef, {});
		}
	}else{ 
		# no body part to parse
		return (undef, undef, {});
	}	  
} 
sub parse_for_f__king_exchange { 
	my $self=shift;
	my $entity = shift; 
	my @parts = $entity->parts; 
	my $email; 
	my $diag = {}; 
	my $list;
	my $state       = 0;
	my $pattern     = 'Your message';
						
	if(!@parts){ 
		if($entity->head->mime_type eq 'text/plain'){ 
			my $body = $entity->bodyhandle; 
			my $IO;
			if($body){ 
				if($IO = $body->open("r")){ # "r" for reading.  
					while (defined($_ = $IO->getline)){ 
						my $data = $_;
						$state = 1 if $data =~ /$pattern/;
						if ($state == 1) {
							$data =~ s/\n/ /g;
							if($data =~ /\s{2}To:\s{6}(\S+\@\S+)/){ 
								$email =  $1;
							}
							elsif($data =~ /(MSEXCH)(.*?)(Unknown\sRecipient|Unknown|)/){ # I know, not perfect.
								$diag->{Guessed_MTA}       = 'Exchange';
								$diag->{'Diagnostic-Code'} = 'Unknown Recipient';
							}else{ 
								#...
								#warn "nope: " . $data; 
							}
						}
					}
				}
			}
		} 
		return ($list, $email, $diag);
	}else{ 
		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			($list, $email, $diag) = $self->parse_for_f__king_exchange($part); 
			if(($email) && (keys %$diag)){ 
				return ($list, $email, $diag); 
			}
		}
	}
}
sub parse_for_novell { #like, really...
	my $self=shift;
	my $entity = shift; 
	my @parts = $entity->parts; 
	my $email; 
	my $diag = {}; 
	my $list;
	my $state       = 0;
	my $pattern     = 'The message that you sent';

	if(!@parts){ 
		if($entity->head->mime_type eq 'text/plain'){ 
			my $body = $entity->bodyhandle; 
			my $IO;
			if($body){ 
				if($IO = $body->open("r")){ # "r" for reading.  
					while (defined($_ = $IO->getline)){ 
						my $data = $_;
						$state = 1 if $data =~ /$pattern/;
						if ($state == 1) {
							$data =~ s/\n/ /g;
							if($data =~ /\s+(\S+\@\S+)\s\((.*?)\)/){ 
								$email                     =  $1;
								$diag->{'Diagnostic-Code'} =  $2;
							}else{ 
								#...
							}
						}
					}
				}
			}
		} 
		return ($list, $email, $diag);
	}else{ 

		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			($list, $email, $diag) = $self->parse_for_novell($part); 
			if(($email) && (keys %$diag)){ 
				$diag->{'X-Mailer'} = find_mailer_bounce_headers($entity);
				return ($list, $email, $diag); 
			}
		}
	}
}
sub find_mailer_bounce_headers { 
	my $entity = shift; 
	my $mailer = $entity->head->get('X-Mailer', 0); 
	   $mailer =~ s/\n//g;
	return $mailer if $mailer; 
}
sub parse_for_gordano { # what... ever that is there...
	my $self=shift;	
	my $entity = shift; 
	my @parts = $entity->parts; 
	my $email; 
	my $diag = {}; 
	my $list;
	my $state       = 0;
	
	my $pattern     = 'Your message to';
	my $end_pattern = 'The message headers';
	
	if(!@parts){ 
		if($entity->head->mime_type eq 'text/plain'){ 
			my $body = $entity->bodyhandle; 
			my $IO;
			if($body){ 
				if($IO = $body->open("r")){ # "r" for reading.  
					while (defined($_ = $IO->getline)){ 
						my $data = $_;
						$state = 1 if $data =~ /$pattern/;
						$state = 0 if $data =~ /$end_pattern/;
						if ($state == 1) {
							$data =~ s/\n/ /g;
							if($data =~ /RCPT To:\<(\S+\@\S+)\>/){	#    RCPT To:<xxx@usnews.com>
								$email                     =  $1;
							}elsif($data =~ /(.*?)\s(\d+\.\d+\.\d+)\s(.*)/){	# 550 5.1.1 No such mail drop defined.
								$diag->{Status}			   = $2; 
								$diag->{'Diagnostic-Code'} = $3;
								$diag->{'Final-Recipient'} = 'rfc822'; #munge; 
								$diag->{Action}            = 'failed'; #munge;
							}else{ 
								#...
							}
						}
					}
				}
			}
		} 
		return ($list, $email, $diag);
	}else{ 
		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			($list, $email, $diag) = $self->parse_for_gordano($part); 
			if(($email) && (keys %$diag)){ 
				$diag->{'X-Mailer'} = find_mailer_bounce_headers($entity);
				return ($list, $email, $diag); 
			}
		}
	}
}
sub parse_for_overquota_yahoo { 
	my $self=shift;
	my $entity = shift; 
	my @parts = $entity->parts; 
	my $email; 
	my $diag = {}; 
	my $list;
	my $state       = 0;
	my $pattern     = 'Message from  yahoo.com.';

	if(!@parts){ 
		if($entity->head->mime_type eq 'text/plain'){ 
			my $body = $entity->bodyhandle; 
			my $IO;
			if($body){ 
				if($IO = $body->open("r")){ # "r" for reading.  
					while (defined($_ = $IO->getline)){ 
						my $data = $_;
						$state = 1 if $data =~ /$pattern/;
						$diag->{'Remote-MTA'} = 'yahoo.com';
						if ($state == 1) {
							$data =~ s/\n/ /g; #what's up with that?	
							if($data =~ /\<(\S+\@\S+)\>\:/){ 
								$email                     =  $1;
							}else{ 
								if($data =~ m/(over quota)/){ 
									$diag->{'Diagnostic-Code'} = $data;
								}
							}
						}
					}
				}
			}
		} 
		return ($list, $email, $diag);
	}else{ 

		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			($list, $email, $diag) = $self->parse_for_overquota_yahoo($part); 
			if(($email) && (keys %$diag)){ 
				$diag->{'X-Mailer'} = find_mailer_bounce_headers($entity);
				return ($list, $email, $diag); 
			}
		}
	}
}
sub parse_for_earthlink { 
	my $self=shift;
	my $entity = shift; 
	my @parts = $entity->parts; 
	my $email; 
	my $diag = {}; 
	my $list;
	my $state       = 0;
	my $pattern     = 'Sorry, unable to deliver your message to';

	if(!@parts){ 
		if($entity->head->mime_type eq 'text/plain'){ 
			my $body = $entity->bodyhandle; 
			my $IO;
			if($body){ 
				if($IO = $body->open("r")){ # "r" for reading.  
					while (defined($_ = $IO->getline)){ 
						my $data = $_;
						$state = 1 if $data =~ /$pattern/;
						if ($state == 1) {
							$diag->{'Remote-MTA'} = 'Earthlink';
							$data =~ s/\n/ /g; #what's up with that?	
							if($data =~ /(\d{3})\s(.*?)\s(\S+\@\S+)/){	#  552 Quota violation for postmaster@example.com
								$diag->{'Diagnostic-Code'} = $1 . ' ' . $2; 
								$email = $3; 
							}
						}
					}
				}
			}
		} 
		return ($list, $email, $diag);
	}else{ 

		my $i;
		foreach $i (0 .. $#parts) {
	    	my $part = $parts[$i];
			#($list, $email, $diag) = parse_for_overquota_yahoo($part); 
			#Probably author mistake
			($list, $email, $diag) = $self->parse_for_earthlink($part); 
			if(($email) && (keys %$diag)){ 
				$diag->{'X-Mailer'} = find_mailer_bounce_headers($entity);
				return ($list, $email, $diag); 
			}
		}
	}
}

sub parse_bounce { 
	my $self=shift;
#	print("parse_bounce print I'm here: ".$self->{is_bounce}."\n");
#	my $message = $self->{}; 
	my $email       = '';
	my $list        = '';
	my $diagnostics = {};
	$self->{diagnostics}=$diagnostics;
	my $entity=$self->{message}; 
	
	if(!$entity){
		$self->log("No MIME entity found, this message could be garbage, skipping");
	}else{ 
#		if($verbose){ 
#			print '-' x 72 . "\n"; 
#			$entity->dump_skeleton; 
#			print '-' x 72 . "\n"; 
#		} 
#		
#		$email = find_verp($entity);
#		$self->log("Verp email $email") if $email;
#		$self->set_bounced_flag($email,$diagnostics,'find_verp');
		my ($gp_list, $gp_email, $gp_diagnostics) = $self->generic_parse($entity); 	
		$list        = $gp_list if $gp_list; 
		$email     ||=  $gp_email; 
		$diagnostics = $gp_diagnostics if $gp_diagnostics;
		$self->set_bounced_flag($email,$diagnostics,'generic_parse');
		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($qmail_list, $qmail_email, $qmail_diagnostics) = $self->parse_for_qmail($entity); 
			$email ||= $qmail_email;
			%{$diagnostics} = (%{$diagnostics}, %{$qmail_diagnostics}) if $qmail_diagnostics; 
		} 
		$self->set_bounced_flag($email,$diagnostics,'parse_for_qmail');
		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($exim_list, $exim_email, $exim_diagnostics) = $self->parse_for_exim($entity); 
			$email ||= $exim_email;
			%{$diagnostics} = (%{$diagnostics}, %{$exim_diagnostics})
				if $exim_diagnostics; 
		}
		$self->set_bounced_flag($email,$diagnostics,'parse_for_exim');
		
		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($ms_list, $ms_email, $ms_diagnostics) = $self->parse_for_f__king_exchange($entity); 
			$email ||= $ms_email;
			%{$diagnostics} = (%{$diagnostics}, %{$ms_diagnostics})
				if $ms_diagnostics; 
		}
		$self->set_bounced_flag($email,$diagnostics,'parse_for_f__king_exchange');
		
		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($nv_list, $nv_email, $nv_diagnostics) = $self->parse_for_novell($entity); 
			$email ||= $nv_email;
			%{$diagnostics} = (%{$diagnostics}, %{$nv_diagnostics})
				if $nv_diagnostics; 
		}
		$self->set_bounced_flag($email,$diagnostics,'parse_for_novell');
		
		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($g_list, $g_email, $g_diagnostics) = $self->parse_for_gordano($entity); 
			$email ||= $g_email;
			%{$diagnostics} = (%{$diagnostics}, %{$g_diagnostics})
				if $g_diagnostics; 
		}
		$self->set_bounced_flag($email,$diagnostics,'parse_for_gordano');
		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($y_list, $y_email, $y_diagnostics) = $self->parse_for_overquota_yahoo($entity); 
			$email ||= $y_email;
			%{$diagnostics} = (%{$diagnostics}, %{$y_diagnostics})
				if $y_diagnostics;
		}	
		$self->set_bounced_flag($email,$diagnostics,'parse_for_overquota_yahoo');		

		if((!$email) || !keys %{$diagnostics}){ 		    
			my ($el_list, $el_email, $el_diagnostics) = $self->parse_for_earthlink($entity); 
			$email ||= $el_email;
			%{$diagnostics} = (%{$diagnostics}, %{$el_diagnostics})
				if $el_diagnostics; 
		}	
		$self->set_bounced_flag($email,$diagnostics,'parse_for_earthlink');
		if($self->is_bounce){
			my $rule_now=$self->find_rule_to_use();
			if (defined $rule_now){
				my $action=$rule_now->{Action};
				foreach my $act_id(keys %$action){
					if ($act_id eq 'is_bounce'){
						$self->{is_bounce}=$action->{$act_id};
					}else{
						$self->{diagnostics}->{"_$act_id"}=$action->{$act_id};
					}
				}
				$self->{diagnostics}->{"_rule_key"}=$rule_now->{key};
			}

			
		}
		return;		
		#small hack, turns, %2 into, '-'
		#$list =~ s/\%2d/\-/g;
		#$list = trim($list); 
		
#		print generate_nerd_report($list, $email, $diagnostics) if $verbose;  
#			my $rule = find_rule_to_use($list, $email, $diagnostics); 
#			print "\nUsing Rule: $rule\n\n" if $verbose; 	
#		if(!bounce_from_me($entity)){			
#			if(!$debug){ 
#				#push(@$Rules_To_Carry_Out, [$rule, $list, $email, $diagnostics, $message]);
#				carry_out_rule($rule, $list, $email, $diagnostics, $message); 
#			} 
#		}else{ 
#			warn "Whoop! Bounced message was sent by myself... kinda going to ignore and delete...";
#		}
	}
	#sleep(1);
}
sub find_rule_to_use{
	my $self=shift;
	my $Rules=$self->GetRules;
	my $diagnostics=$self->diagnostics;
	RULES: foreach my $rule(@$Rules){
		my $Title=$rule->{key};
		next unless length($Title);
		my $examine = $rule->{Examine}; 
		my $message_fields = $examine->{Message_Fields};
		my %ThingsToMatch; 
		foreach my $m_field(keys %$message_fields){ 
			my $is_regex   = 0; 
			my $real_field = $m_field; 
			$ThingsToMatch{$m_field} = 0; 
			if($m_field =~ m/_regex$/){ 
				$is_regex = 1; 
				$real_field = $m_field; 
				$real_field =~ s/_regex$//;  
			}
			MESSAGEFIELD: foreach my $pos_match(@{$message_fields->{$m_field}}){ 
				if($is_regex == 1){ 
					if($diagnostics->{$real_field} =~ m/$pos_match/){ 	
						$ThingsToMatch{$m_field} = 1;
						next MESSAGEFIELD;
					}				
				}else{ 
				
					if($diagnostics->{$real_field} eq $pos_match){ 	
						$ThingsToMatch{$m_field} = 1;
						next MESSAGEFIELD;
					}
				
				}
			}
		}
		foreach(keys %ThingsToMatch){ 
			if($ThingsToMatch{$_} == 0){
				next RULES; 
			}
		}
		return $rule; 		
	}
	return undef;
}
sub GetRules{
	my $self=shift;
	my $Rules = [
          {
            'Action' => {
                          'is_bounce' => 0,
			  'note' => 'Qmail delivery delay notification - not bounced'
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:The mail system will continue delivery attempts)/
                                                                            ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail_delivery_delay_notification'
          },
	  {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
						'Guessed_MTA' => [
                                                                    'Exim'
                                                                  ],
                                                 'Action' => [
                                                               'failed',
                                                               'Failed'
                                                             ],
                                                 'Status' => [
                                                               '5.4.4',
                                                             ]
                                               }
                         },
            'key' => 'exim_user_unroutble_host'
          },	  
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:552|exceeded storage allocation|over quota|mailbox full|disk quota exceeded|Mail quota exceeded|Quota violation)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed',
                                                               'Failed'
                                                             ],
                                                 'Status' => [
                                                               '5.2.2',
                                                               '4.2.2',
                                                               '5.0.0',
                                                               '5.1.1'
                                                             ]
                                               }
                         },
            'key' => 'over_quota'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:larger than the current system limit)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.2.3'
                                                             ]
                                               }
                         },
            'key' => 'hotmail_over_quota'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:LOCAL;<>)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.0.0'
                                                             ]
                                               }
                         },
            'key' => 'over_quota_obscure_mta'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '4.2.2'
                                                             ]
                                               }
                         },
            'key' => 'over_quota_obscure_mta_two'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:over quota)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Remote-MTA_regex' => [
                                                                         qr/(?-xism:yahoo.com)/
                                                                       ],
                                                 'Status' => [
                                                               '5.0.0'
                                                             ]
                                               }
                         },
            'key' => 'yahoo_over_quota'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Remote-MTA' => [
                                                                   'yahoo.com'
                                                                 ],
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:over quota)/
                                                                            ]
                                               }
                         },
            'key' => 'yahoo_over_quota_two'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:mailbox is full|Exceeded storage allocation|mailbox full|storage full)/
                                                                            ],
                                                 'Status' => [
                                                               '5.2.2',
                                                               '5.x.y'
                                                             ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail_over_quota'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Action' => [
                                                               'Failed',
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               qr/(?-xism:mailbox full)/
                                                             ]
                                               }
                         },
            'key' => 'status_over_quota'
          },
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Remote-MTA' => [
                                                                   'Earthlink'
                                                                 ],
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:522|Quota violation)/
                                                                            ]
                                               }
                         },
            'key' => 'earthlink_over_quota'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:551)/
                                                                            ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail_error_5dot5dot1'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:no mailbox here by that name)/
                                                                            ],
                                                 'Status' => [
                                                               '5.1.1'
                                                             ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail2_error_5dot5dot1'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:SMTP; 550|550 MAILBOX NOT FOUND|550 5\.1\.1 unknown or illegal alias|User unknown|No such mail drop)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.1.1'
                                                             ]
                                               }
                         },
            'key' => 'delivery_error_550'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.1.1'
                                                             ]
                                               }
                         },
            'key' => 'delivery_error_5dot5dot1_status'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:554 delivery error)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.0.0'
                                                             ]
                                               }
                         },
            'key' => 'delivery_error_554'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ],
                                                 'Status' => [
                                                               '5.x.y'
                                                             ]
                                               }
                         },
            'key' => 'qmail_user_unknown'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:554)/
                                                                            ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail_error_554'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:550)/
                                                                            ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail_error_550'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ],
                                                 'Status' => [
                                                               '5.1.2'
                                                             ]
                                               }
                         },
            'key' => 'qmail_unknown_domain'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:This address no longer accepts mail.)/
                                                                            ],
                                                 'Guessed_MTA' => [
                                                                    'Qmail'
                                                                  ]
                                               }
                         },
            'key' => 'qmail_bounce_saying'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Guessed_MTA' => [
                                                                    'Exim'
                                                                  ],
                                                 'Status' => [
                                                               '5.x.y'
                                                             ]
                                               }
                         },
            'key' => 'exim_user_unknown'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:Unknown Recipient)/
                                                                            ],
                                                 'Guessed_MTA' => [
                                                                    'Exchange'
                                                                  ]
                                               }
                         },
            'key' => 'exchange_user_unknown'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:250 OK)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Reporting-MTA_regex' => [
                                                                            qr/(?-xism:aol\.com)/
                                                                          ],
                                                 'Status' => [
                                                               '2.0.0'
                                                             ]
                                               }
                         },
            'key' => 'aol_user_unknown'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:No such user|Addressee unknown)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.3.0'
                                                             ]
                                               }
                         },
            'key' => 'user_unknown_5dot3dot0_status'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:user inactive)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.0.0'
                                                             ]
                                               }
                         },
            'key' => 'user_inactive'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Guessed_MTA' => [
                                                                    'Postfix'
                                                                  ],
                                                 'Status' => [
                                                               '5.0.0'
                                                             ]
                                               }
                         },
            'key' => 'postfix_5dot0dot0_error'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Diagnostic-Code_regex' => [
                                                                              qr/(?-xism:551 not our customer|User unknown)/
                                                                            ],
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.1.6'
                                                             ]
                                               }
                         },
            'key' => 'permanent_move_failure'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'Final-Recipient_regex' => [
                                                                              qr/(?-xism:822)/
                                                                            ],
                                                 'Action' => [
                                                               'failed'
                                                             ],
                                                 'Status' => [
                                                               '5.1.2'
                                                             ]
                                               }
                         },
            'key' => 'unknown_domain'
          },
          {
            'Action' => {
                          'hardsoft' => 'Hard',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                 'FoundBy' => [
                                                               'generic_parse'
                                                             ],
                                                 'Diagnostic-Code_regex' => [
                                                               qr/spam|refused|rejected|(?:\(RTR:BL\))|(?:domain\s+(?:isn't|not)\s+allowed)|blacklisted|IP\saddress\sdenied/i
                                                             ]		     
                                               }
                         },
            'key' => 'generic_parse_spam_reject'
          },	  
          {
            'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1
                        },
            'Examine' => {
                           'Message_Fields' => {
                                                'Status' => [
                                                               "4.4.7"
                                                             ]		     
                                               }
                         },
            'key' => 'delivery_time_expired'
          },
	  
          {
		'Action' => {
                          'hardsoft' => 'Soft',
                          'is_bounce' => 1,
			  'note' => 'Unknown bounce type'
                        },
            'Examine' => {},
            'key' => 'unknown_bounce_type'
          },
        ];
	
	return($Rules)
}

1;
